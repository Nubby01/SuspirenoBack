"""Vistas del panel: productos, insumos, cotizaciones, pedidos y cuentas."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count, ProtectedError, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from django.contrib.auth import update_session_auth_hash

from ..forms import (
    AyudanteEditarForm,
    AyudanteForm,
    CambiarClaveForm,
    CompraForm,
    ConvertirPedidoForm,
    CotizacionEditarForm,
    InsumoForm,
    PedidoEditarForm,
    PedidoManualForm,
    ProductoForm,
    RecetaForm,
)
from ..mixins import EliminarModalMixin, FormularioMixin, PanelMixin, SoloAdministradoraMixin
from ..models import Cliente, Cotizacion, CotizacionProducto, Insumo, Pedido, PedidoProducto, Producto, ProductoInsumo, Usuario
from ..reglas import ReglaNegocioError, cambiar_estado, convertir_cotizacion, registrar_compra
from ..whatsapp import enlace_whatsapp


class ProductoListaView(PanelMixin, ListView):
    template_name = "panel/productos.html"
    context_object_name = "productos"

    def get_queryset(self):
        productos = (
            Producto.objects.annotate(
                veces_cotizado=Count("lineas_cotizacion", distinct=True),
                unidades_pedidas=Sum("lineas_pedido__cantidad"),
            )
            .prefetch_related("receta__insumo")
            .order_by("nombre")
        )
        q = self.request.GET.get("q", "").strip()
        categoria = self.request.GET.get("categoria", "").strip()
        if q:
            productos = productos.filter(nombre__icontains=q)
        if categoria:
            productos = productos.filter(categoria=categoria)
        return productos

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["q"] = self.request.GET.get("q", "")
        contexto["categoria"] = self.request.GET.get("categoria", "")
        contexto["categorias"] = Producto.CATEGORIAS
        return contexto


class ProductoCrearView(SoloAdministradoraMixin, FormularioMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "panel/producto_form.html"
    titulo = "Nuevo producto"
    volver_url = "productos"
    success_url = reverse_lazy("productos")


class ProductoEditarView(SoloAdministradoraMixin, FormularioMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "panel/producto_form.html"
    titulo = "Editar producto"
    volver_url = "productos"
    success_url = reverse_lazy("productos")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["receta_form"] = RecetaForm()
        contexto["receta"] = self.object.receta.select_related("insumo")
        return contexto


class ProductoEliminarView(SoloAdministradoraMixin, EliminarModalMixin, FormularioMixin, DeleteView):
    model = Producto
    template_name = "panel/formulario.html"
    titulo = "Eliminar producto"
    volver_url = "productos"
    success_url = reverse_lazy("productos")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "No se puede eliminar: ya está en una cotización, un pedido o una receta guardada.")
            return redirect(self.success_url)


class RecetaAgregarView(SoloAdministradoraMixin, FormularioMixin, CreateView):
    form_class = RecetaForm
    template_name = "panel/formulario.html"
    titulo = "Agregar insumo a la receta"

    def dispatch(self, request, *args, **kwargs):
        self.producto = get_object_or_404(Producto, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["volver"] = reverse("producto_editar", args=[self.producto.pk])
        return contexto

    def form_valid(self, form):
        form.instance.producto = self.producto
        try:
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "Ese insumo ya está en la receta.")
            return redirect("producto_editar", pk=self.producto.pk)

    def get_success_url(self):
        return f"/panel/productos/{self.producto.pk}/editar/"


class RecetaQuitarView(SoloAdministradoraMixin, EliminarModalMixin, DeleteView):
    model = ProductoInsumo
    template_name = "panel/formulario.html"
    volver_url = "productos"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["titulo"] = "Quitar insumo de la receta"
        contexto["volver"] = f"/panel/productos/{self.object.producto_id}/editar/"
        return contexto

    def get_success_url(self):
        return f"/panel/productos/{self.object.producto_id}/editar/"


class InsumoListaView(PanelMixin, ListView):
    model = Insumo
    template_name = "panel/insumos.html"
    context_object_name = "insumos"


class InsumoCrearView(SoloAdministradoraMixin, FormularioMixin, CreateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "panel/formulario.html"
    titulo = "Nuevo insumo"
    volver_url = "insumos"
    success_url = reverse_lazy("insumos")


class InsumoEditarView(SoloAdministradoraMixin, FormularioMixin, UpdateView):
    model = Insumo
    form_class = InsumoForm
    template_name = "panel/formulario.html"
    titulo = "Editar insumo"
    volver_url = "insumos"
    success_url = reverse_lazy("insumos")


class InsumoDetalleView(PanelMixin, DetailView):
    model = Insumo
    template_name = "panel/insumo_detalle.html"
    context_object_name = "insumo"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["compras"] = self.object.compras.all()
        contexto["form"] = CompraForm()
        contexto["usos"] = (
            PedidoProducto.objects.filter(
                producto__receta__insumo=self.object,
                pedido__stock_descontado=True,
            )
            .select_related("pedido", "producto", "pedido__cotizacion__cliente")
            .order_by("-pedido__fecha_pedido", "-id")[:30]
        )
        return contexto


class InsumoEliminarView(SoloAdministradoraMixin, EliminarModalMixin, FormularioMixin, DeleteView):
    model = Insumo
    template_name = "panel/formulario.html"
    titulo = "Eliminar insumo"
    volver_url = "insumos"
    success_url = reverse_lazy("insumos")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "No se puede eliminar: está en una receta o en una compra.")
            return redirect(self.success_url)


@login_required
@require_POST
def compra_registrar(request, pk):
    if not request.user.es_administradora:
        raise PermissionDenied
    insumo = get_object_or_404(Insumo, pk=pk)
    form = CompraForm(request.POST)
    if form.is_valid():
        registrar_compra(insumo, form.cleaned_data)
        messages.success(request, "Compra registrada y stock actualizado.")
        return redirect("insumo_detalle", pk=pk)
    return render(request, "panel/insumo_detalle.html", {
        "insumo": insumo,
        "compras": insumo.compras.all(),
        "form": form,
    })


class CotizacionListaAdminView(PanelMixin, ListView):
    template_name = "panel/cotizaciones.html"
    context_object_name = "cotizaciones"

    def get_queryset(self):
        return Cotizacion.objects.select_related("cliente").prefetch_related("lineas")


class CotizacionDetalleView(PanelMixin, DetailView):
    template_name = "panel/cotizacion_detalle.html"
    context_object_name = "cotizacion"

    def get_queryset(self):
        return Cotizacion.objects.select_related("cliente").prefetch_related("lineas__producto")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["form"] = ConvertirPedidoForm()
        contexto["whatsapp"] = enlace_whatsapp(self.object)
        return contexto


class CotizacionEditarView(PanelMixin, View):
    template_name = "panel/cotizacion_editar.html"

    def get_cotizacion(self, pk):
        return get_object_or_404(
            Cotizacion.objects.select_related("cliente").prefetch_related("lineas__producto"),
            pk=pk,
        )

    def get(self, request, pk):
        cotizacion = self.get_cotizacion(pk)
        return render(request, self.template_name, {
            "cotizacion": cotizacion,
            "form": CotizacionEditarForm(cotizacion=cotizacion),
            "titulo": f"Editar cotización {cotizacion.pk}",
            "volver": reverse("cotizacion_detalle", args=[cotizacion.pk]),
        })

    def post(self, request, pk):
        cotizacion = self.get_cotizacion(pk)
        form = CotizacionEditarForm(request.POST, cotizacion=cotizacion)
        if form.is_valid():
            form.save()
            messages.success(request, "Cotización actualizada.")
            return redirect("cotizacion_detalle", pk=cotizacion.pk)
        return render(request, self.template_name, {
            "cotizacion": cotizacion,
            "form": form,
            "titulo": f"Editar cotización {cotizacion.pk}",
            "volver": reverse("cotizacion_detalle", args=[cotizacion.pk]),
        })


class PedidoListaView(PanelMixin, ListView):
    template_name = "panel/pedidos.html"
    context_object_name = "pedidos"

    def get_queryset(self):
        return Pedido.objects.con_detalle()


class PedidoDetalleView(PanelMixin, DetailView):
    template_name = "panel/pedido_detalle.html"
    context_object_name = "pedido"

    def get_queryset(self):
        return Pedido.objects.con_detalle().prefetch_related("lineas__producto__receta__insumo")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["form_editar"] = PedidoEditarForm(instance=self.object)
        return contexto


class PedidoManualView(SoloAdministradoraMixin, View):
    template_name = "panel/pedido_manual.html"

    def get(self, request):
        return render(request, self.template_name, {"form": PedidoManualForm()})

    def post(self, request):
        form = PedidoManualForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        datos = form.cleaned_data
        producto = datos["producto"]
        variante = producto.variantes.order_by("orden", "id").first()
        precio = variante.precio if variante else producto.precio
        formato = datos["formato"] or (variante.formato if variante else "")
        cantidad = datos["cantidad"]
        total = precio * cantidad
        cliente, _ = Cliente.objects.get_or_create(
            telefono=datos["telefono"],
            defaults={"nombre": datos["nombre"], "direccion": datos["direccion"]},
        )
        if datos["direccion"]:
            cliente.nombre = datos["nombre"]
            cliente.direccion = datos["direccion"]
            cliente.save()
        try:
            with transaction.atomic():
                cotizacion = Cotizacion.objects.create(cliente=cliente, total=total, estado=Cotizacion.ENVIADA)
                CotizacionProducto.objects.create(
                    cotizacion=cotizacion,
                    producto=producto,
                    formato=formato,
                    cantidad=cantidad,
                    precio=precio,
                    subtotal=total,
                )
                pedido = convertir_cotizacion(
                    cotizacion,
                    request.user,
                    datos["fecha_entrega"],
                    datos["abono"],
                    datos["canal_despacho"],
                )
                if datos["estado"] != Pedido.PENDIENTE:
                    pedido.estado = datos["estado"]
                    pedido.save(update_fields=["estado"])
        except ReglaNegocioError as error:
            form.add_error(None, str(error))
            return render(request, self.template_name, {"form": form})
        messages.success(request, f"Pedido {pedido.pk} registrado.")
        return redirect("pedido_detalle", pk=pedido.pk)


class PedidoEditarView(PanelMixin, FormularioMixin, UpdateView):
    model = Pedido
    form_class = PedidoEditarForm
    template_name = "panel/formulario.html"
    titulo = "Editar pedido"
    volver_url = "pedidos"
    success_url = reverse_lazy("pedidos")

    def form_valid(self, form):
        messages.success(self.request, "Pedido actualizado.")
        return super().form_valid(form)


class PedidoEliminarView(PanelMixin, EliminarModalMixin, FormularioMixin, DeleteView):
    model = Pedido
    template_name = "panel/formulario.html"
    titulo = "Eliminar pedido"
    volver_url = "pedidos"
    success_url = reverse_lazy("pedidos")


class CotizacionEliminarView(SoloAdministradoraMixin, EliminarModalMixin, FormularioMixin, DeleteView):
    model = Cotizacion
    template_name = "panel/formulario.html"
    titulo = "Eliminar cotización"
    volver_url = "cotizaciones"
    success_url = reverse_lazy("cotizaciones")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "No se puede eliminar: ya tiene un pedido asociado.")
            return redirect(self.success_url)


@login_required
@require_POST
def cotizacion_convertir(request, pk):
    if not request.user.es_administradora:
        raise PermissionDenied
    cotizacion = get_object_or_404(
        Cotizacion.objects.select_related("cliente").prefetch_related("lineas__producto__receta__insumo"),
        pk=pk,
    )
    form = ConvertirPedidoForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                pedido = convertir_cotizacion(cotizacion, request.user, **form.cleaned_data)
        except ReglaNegocioError as error:
            form.add_error(None, str(error))
        else:
            messages.success(request, f"Pedido {pedido.pk} creado.")
            return redirect("pedido_detalle", pk=pedido.pk)
    return render(request, "panel/cotizacion_detalle.html", {
        "cotizacion": cotizacion,
        "form": form,
        "whatsapp": enlace_whatsapp(cotizacion),
    })


@login_required
@require_POST
def pedido_estado(request, pk):
    if not request.user.entra_al_panel:
        raise PermissionDenied
    pedido = get_object_or_404(Pedido.objects.prefetch_related("lineas__producto__receta__insumo"), pk=pk)
    try:
        with transaction.atomic():
            cambiar_estado(pedido, request.POST.get("estado", ""))
    except (ReglaNegocioError, KeyError) as error:
        messages.error(request, str(error) or "Ese cambio de estado no está permitido.")
        return redirect("pedido_detalle", pk=pk)
    messages.success(request, f"El pedido quedó en {pedido.estado}.")
    return redirect("pedido_detalle", pk=pk)


class UsuarioListaView(SoloAdministradoraMixin, ListView):
    template_name = "panel/usuarios.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        return Usuario.objects.order_by("rol", "username")

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        cuentas = list(contexto["usuarios"])
        contexto["clientes"] = [cuenta for cuenta in cuentas if cuenta.rol == Usuario.PENDIENTE]
        contexto["equipo"] = [cuenta for cuenta in cuentas if cuenta.rol != Usuario.PENDIENTE]
        contexto["form_ayudante"] = AyudanteForm(admin=self.request.user)
        return contexto


class UsuarioEliminarView(SoloAdministradoraMixin, EliminarModalMixin, FormularioMixin, DeleteView):
    model = Usuario
    template_name = "panel/formulario.html"
    titulo = "Eliminar cuenta"
    volver_url = "usuarios"
    success_url = reverse_lazy("usuarios")

    def get_queryset(self):
        return Usuario.objects.exclude(pk=self.request.user.pk)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Cuenta eliminada.")
        return super().delete(request, *args, **kwargs)


class AyudanteEditarView(SoloAdministradoraMixin, FormularioMixin, UpdateView):
    model = Usuario
    form_class = AyudanteEditarForm
    template_name = "panel/formulario.html"
    titulo = "Editar ayudante"
    volver_url = "usuarios"
    success_url = reverse_lazy("usuarios")

    def get_queryset(self):
        return Usuario.objects.filter(rol=Usuario.AYUDANTE)

    def form_valid(self, form):
        messages.success(self.request, "Datos del ayudante actualizados.")
        return super().form_valid(form)


class PanelCuentaView(PanelMixin, View):
    template_name = "panel/cuenta.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "form_clave": CambiarClaveForm(request.user),
                "obligar_clave": request.user.debe_cambiar_clave,
            },
        )

    def post(self, request):
        form = CambiarClaveForm(request.user, request.POST)
        if form.is_valid():
            cambio = bool(form.cleaned_data.get("new_password1"))
            usuario = form.save()
            if cambio:
                update_session_auth_hash(request, usuario)
                messages.success(request, "La clave quedó actualizada.")
                if usuario.entra_al_panel:
                    return redirect("reportes")
            else:
                messages.success(request, "La clave actual es correcta.")
            return redirect("panel_cuenta")
        return render(
            request,
            self.template_name,
            {"form_clave": form, "obligar_clave": request.user.debe_cambiar_clave},
        )


@login_required
@require_POST
def usuario_crear_ayudante(request):
    if not request.user.es_administradora:
        raise PermissionDenied
    form = AyudanteForm(request.POST, admin=request.user)
    if form.is_valid():
        datos = form.cleaned_data
        Usuario.objects.create_user(
            username=datos["username"],
            password=datos["password1"],
            first_name=datos["nombre"],
            rol=Usuario.AYUDANTE,
            debe_cambiar_clave=True,
        )
        messages.success(
            request,
            f"Ayudante {datos['username']} creado con clave provisoria. Deberá cambiarla al ingresar por primera vez.",
        )
        return redirect("usuarios")
    mensajes = []
    for errores in form.errors.values():
        mensajes.extend(errores)
    messages.error(request, " ".join(str(mensaje) for mensaje in mensajes) or "No se pudo crear el ayudante.")
    return redirect("usuarios")
