"""Vistas públicas: inicio, catálogo, cotización y cuentas."""

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView

from ..forms import CambiarClaveForm, CotizacionClienteForm, IngresoForm, RegistroForm
from ..menu import BANNER, FESTIVAS, GRUPOS_NAV
from ..models import Cliente, Cotizacion, CotizacionProducto, Pedido, Producto, Usuario
from ..reglas import faltantes_de
from ..whatsapp import enlace_whatsapp

CANTIDAD_MAXIMA = 100

CATEGORIAS_POR_GRUPO = {
    grupo["etiqueta"]: [valor for valor, _ in grupo.get("hijos", [])] if grupo.get("hijos") else [grupo["valor"]]
    for grupo in GRUPOS_NAV
}


def _carrito(request):
    return {str(clave): int(valor) for clave, valor in request.session.get("carrito", {}).items()}


def _guardar_carrito(request, carrito):
    request.session["carrito"] = carrito
    request.session.modified = True


def _recordar_cotizacion(request, cotizacion):
    propias = list(request.session.get("cotizaciones_propias", []))
    if cotizacion.pk not in propias:
        propias.append(cotizacion.pk)
    request.session["cotizaciones_propias"] = propias
    request.session["ultima_cotizacion"] = cotizacion.pk
    request.session.modified = True


def reclamar_cotizaciones(request):
    if not request.user.is_authenticated:
        return
    propias = list(request.session.get("cotizaciones_propias", []))
    ultima = request.session.get("ultima_cotizacion")
    if ultima and ultima not in propias:
        propias.append(ultima)
    if not propias:
        return
    Cotizacion.objects.filter(pk__in=propias, creada_por__isnull=True).update(creada_por=request.user)


DESTACADOS = [
    "Rollos de canela",
    "Alfajor brownie manjar",
    "Mantequilla de maní",
    "Pie de limón",
]

RESEÑAS = [
    {
        "nombre": "Camila Soto",
        "texto": "Pedí rollos de canela y una torta de yogurt. Llegaron a la hora y el sabor es el de siempre.",
    },
    {
        "nombre": "Ana Riquelme",
        "texto": "Los alfajores de maní y el pie de limón fueron el pedido de cumpleaños. Volveré a encargar.",
    },
    {
        "nombre": "Josefina Vera",
        "texto": "Armé la cotización desde la página y coordinamos por WhatsApp. Todo quedó claro desde el primer mensaje.",
    },
]


class InicioView(TemplateView):
    template_name = "inicio.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        catalogo = Producto.objects.filter(disponible=True).prefetch_related("receta__insumo", "variantes")
        destacados = list(catalogo.filter(nombre__in=DESTACADOS))
        destacados.sort(key=lambda producto: DESTACADOS.index(producto.nombre) if producto.nombre in DESTACADOS else 99)
        vendidos = list(
            catalogo.filter(lineas_pedido__pedido__estado__in=[Pedido.CONFIRMADO, Pedido.EN_PREPARACION, Pedido.LISTO, Pedido.ENTREGADO])
            .annotate(unidades=Sum("lineas_pedido__cantidad"))
            .order_by("-unidades")[:4]
        )
        if len(vendidos) < 4:
            extras = catalogo.exclude(pk__in=[producto.pk for producto in vendidos])[: 4 - len(vendidos)]
            vendidos.extend(extras)
        contexto.update({
            "destacados": destacados[:4],
            "vendidos": vendidos[:4],
            "resenas": RESEÑAS,
            "banner": BANNER,
        })
        return contexto


class CatalogoView(TemplateView):
    template_name = "catalogo.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        productos = Producto.objects.filter(disponible=True).prefetch_related("receta__insumo", "variantes")
        texto = self.request.GET.get("q", "").strip()
        categoria = self.request.GET.get("categoria", "").strip()
        grupo = self.request.GET.get("grupo", "").strip()
        if texto:
            # Búsqueda por nombre en todo el catálogo
            productos = productos.filter(nombre__icontains=texto)
            categoria = ""
            grupo = ""
        elif categoria:
            productos = productos.filter(categoria=categoria)
        elif grupo in CATEGORIAS_POR_GRUPO:
            productos = productos.filter(categoria__in=CATEGORIAS_POR_GRUPO[grupo])
        else:
            productos = productos.exclude(categoria__in=FESTIVAS)
        contexto.update({
            "productos": productos,
            "q": texto,
            "categoria": categoria,
            "grupo": grupo,
        })
        return contexto


def _variante_de(producto, valor):
    variantes = list(producto.variantes.all())
    if not variantes:
        return None
    elegida = next((variante for variante in variantes if str(variante.pk) == str(valor)), None)
    return elegida or variantes[0]


def _clave_carrito(producto, variante):
    if variante is None:
        return str(producto.pk)
    return f"{producto.pk}:{variante.pk}"


def _pide_json(request):
    aceptar = request.headers.get("Accept", "")
    return (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in aceptar
    )


def _respuesta_carrito(request, *, ok, mensaje, carrito=None):
    cantidad = sum((carrito or _carrito(request)).values())
    if _pide_json(request):
        return JsonResponse({"ok": ok, "mensaje": mensaje, "carrito_cantidad": cantidad})
    if ok:
        messages.success(request, mensaje)
    else:
        messages.error(request, mensaje)
    return redirect(request.POST.get("next") or "catalogo")


@require_POST
def carrito_agregar(request, pk):
    producto = get_object_or_404(Producto.objects.prefetch_related("receta__insumo", "variantes"), pk=pk)
    if producto.sin_stock:
        return _respuesta_carrito(request, ok=False, mensaje=f"{producto.nombre} no está disponible.")
    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except ValueError:
        cantidad = 1
    cantidad = min(CANTIDAD_MAXIMA, max(1, cantidad))
    variante = _variante_de(producto, request.POST.get("variante"))
    eleccion = (request.POST.get("opcion") or "").strip()
    opciones = producto.lista_opciones()
    if opciones and eleccion not in opciones["elecciones"]:
        return _respuesta_carrito(
            request,
            ok=False,
            mensaje=f"Para agregar {producto.nombre} debes marcar {opciones['etiqueta'].lower()}.",
        )
    clave = _clave_carrito(producto, variante)
    if eleccion:
        clave = f"{clave}:{eleccion}"
    carrito = _carrito(request)
    carrito[clave] = min(CANTIDAD_MAXIMA, carrito.get(clave, 0) + cantidad)
    _guardar_carrito(request, carrito)
    extras = []
    if variante:
        extras.append(variante.formato)
    if eleccion:
        extras.append(eleccion)
    detalle = f" ({', '.join(extras)})" if extras else ""
    return _respuesta_carrito(
        request,
        ok=True,
        mensaje=f"Agregaste {producto.nombre}{detalle} a la cotización.",
        carrito=carrito,
    )


@require_POST
def carrito_cambiar(request, clave):
    carrito = _carrito(request)
    if clave not in carrito:
        return redirect("cotizacion")
    try:
        cantidad = int(request.POST.get("cantidad", 1))
    except ValueError:
        cantidad = 1
    if cantidad < 1:
        carrito.pop(clave, None)
    else:
        carrito[clave] = min(CANTIDAD_MAXIMA, cantidad)
    _guardar_carrito(request, carrito)
    return redirect("cotizacion")


class CotizacionView(View):
    template_name = "cotizacion.html"

    def lineas(self, request):
        carrito = _carrito(request)
        pares = []
        for clave, cantidad in carrito.items():
            partes = clave.split(":")
            producto_id = partes[0]
            variante_id = partes[1] if len(partes) > 1 and partes[1].isdigit() else ""
            eleccion = ""
            if len(partes) > 1 and not partes[1].isdigit():
                eleccion = partes[1]
            elif len(partes) > 2:
                eleccion = ":".join(partes[2:]) if partes[1].isdigit() else ":".join(partes[1:])
            if producto_id.isdigit():
                pares.append((clave, producto_id, variante_id, eleccion, cantidad))
        productos = {
            str(producto.pk): producto
            for producto in Producto.objects.prefetch_related("receta__insumo", "variantes").filter(
                pk__in=[producto_id for _, producto_id, _, _, _ in pares]
            )
        }
        resultado = []
        for clave, producto_id, variante_id, eleccion, cantidad in pares:
            producto = productos.get(producto_id)
            if producto is None:
                continue
            variante = _variante_de(producto, variante_id) if variante_id else None
            precio = variante.precio if variante else producto.precio
            formato = variante.formato if variante else ""
            if eleccion:
                formato = f"{formato} · {eleccion}".strip(" ·")
            resultado.append({
                "clave": clave,
                "producto": producto,
                "formato": formato,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": precio * cantidad,
            })
        return resultado

    def formulario_cliente(self, request, datos=None):
        inicial = {}
        if request.user.is_authenticated and request.user.get_full_name():
            inicial["nombre"] = request.user.get_full_name()
        return CotizacionClienteForm(datos, initial=inicial)

    def get(self, request):
        lineas = self.lineas(request)
        ultima = None
        pk = request.session.get("ultima_cotizacion")
        if pk:
            ultima = Cotizacion.objects.filter(pk=pk).select_related("cliente").prefetch_related("lineas__producto").first()
        return render(request, self.template_name, {
            "lineas": lineas,
            "total": sum(linea["subtotal"] for linea in lineas),
            "form": self.formulario_cliente(request),
            "ultima": ultima,
        })

    def post(self, request):
        lineas = self.lineas(request)
        form = self.formulario_cliente(request, request.POST)
        if not lineas:
            messages.error(request, "Agrega al menos un producto desde el catálogo.")
            return redirect("catalogo")
        if not form.is_valid():
            return render(request, self.template_name, {
                "lineas": lineas,
                "total": sum(linea["subtotal"] for linea in lineas),
                "form": form,
            })
        pares = [(linea["producto"], linea["cantidad"]) for linea in lineas]
        faltantes = faltantes_de(pares)
        if faltantes:
            messages.error(request, "No podemos preparar esa cantidad ahora. Prueba con menos unidades.")
            return redirect("cotizacion")
        datos = form.cleaned_data
        cliente, creado = Cliente.objects.get_or_create(
            telefono=datos["telefono"],
            defaults={"nombre": datos["nombre"], "direccion": datos["direccion"]},
        )
        if not creado:
            cliente.nombre = datos["nombre"]
            if datos["direccion"]:
                cliente.direccion = datos["direccion"]
            cliente.save()
        cotizacion = Cotizacion.objects.create(
            cliente=cliente,
            total=sum(linea["subtotal"] for linea in lineas),
            creada_por=request.user if request.user.is_authenticated else None,
        )
        CotizacionProducto.objects.bulk_create([
            CotizacionProducto(
                cotizacion=cotizacion,
                producto=linea["producto"],
                formato=linea["formato"],
                cantidad=linea["cantidad"],
                precio=linea["precio"],
                subtotal=linea["subtotal"],
            )
            for linea in lineas
        ])
        _guardar_carrito(request, {})
        _recordar_cotizacion(request, cotizacion)
        return redirect("cotizacion_lista")


class CotizacionListaView(TemplateView):
    template_name = "cotizacion_lista.html"

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk") or request.session.get("ultima_cotizacion")
        cotizacion = Cotizacion.objects.filter(pk=pk).select_related("cliente").prefetch_related("lineas__producto").first()
        if cotizacion is None:
            return redirect("catalogo")
        propias = request.session.get("cotizaciones_propias", [])
        es_propia = cotizacion.pk in propias or cotizacion.pk == request.session.get("ultima_cotizacion")
        if request.user.is_authenticated and cotizacion.creada_por_id == request.user.pk:
            es_propia = True
        if not es_propia and not (request.user.is_authenticated and request.user.entra_al_panel):
            messages.error(request, "No encontramos esa cotización en tu sesión.")
            return redirect("cotizacion")
        return render(request, self.template_name, {
            "cotizacion": cotizacion,
            "whatsapp": enlace_whatsapp(cotizacion),
        })


class RegistroView(FormView):
    form_class = RegistroForm
    template_name = "cuentas/registro.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("reportes" if request.user.entra_al_panel else "mi_cuenta")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Cuenta creada. Ya puedes ingresar.")
        return redirect("login")

    def form_invalid(self, form):
        messages.error(self.request, "Revisa los datos del formulario para crear la cuenta.")
        return super().form_invalid(form)


class IngresarView(LoginView):
    authentication_form = IngresoForm
    template_name = "cuentas/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.debe_cambiar_clave:
            return reverse("panel_cuenta")
        if self.request.user.rol == Usuario.PENDIENTE:
            return reverse("mi_cuenta")
        return reverse("reportes")

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        reclamar_cotizaciones(self.request)
        if self.request.user.debe_cambiar_clave:
            messages.warning(
                self.request,
                "Tu clave es provisoria. Cámbiala ahora para poder usar el panel.",
            )
        else:
            messages.success(self.request, "Sesión iniciada con éxito.")
        return respuesta

    def form_invalid(self, form):
        messages.error(self.request, "No se pudo iniciar sesión. Revisa usuario y clave.")
        return super().form_invalid(form)


class SalirView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, "Sesión cerrada con éxito.")
        return super().dispatch(request, *args, **kwargs)


class MiCuentaView(LoginRequiredMixin, View):
    template_name = "cuentas/mi_cuenta.html"

    def contexto(self, request, form):
        return {
            "form_clave": form,
            "cotizaciones": Cotizacion.objects.filter(creada_por=request.user)
            .select_related("cliente")
            .prefetch_related("lineas__producto"),
            "pedidos": Pedido.objects.filter(cotizacion__creada_por=request.user)
            .select_related("cotizacion__cliente"),
            "ultima": Cotizacion.objects.filter(pk=request.session.get("ultima_cotizacion"))
            .select_related("cliente")
            .prefetch_related("lineas__producto")
            .first(),
        }

    def get(self, request):
        if request.user.entra_al_panel:
            return redirect("panel_cuenta")
        reclamar_cotizaciones(request)
        return render(request, self.template_name, self.contexto(request, CambiarClaveForm(request.user)))

    def post(self, request):
        if request.user.entra_al_panel:
            return redirect("panel_cuenta")
        form = CambiarClaveForm(request.user, request.POST)
        if form.is_valid():
            cambio = bool(form.cleaned_data.get("new_password1"))
            usuario = form.save()
            if cambio:
                update_session_auth_hash(request, usuario)
                messages.success(request, "La clave quedó actualizada.")
            else:
                messages.success(request, "La clave actual es correcta.")
            return redirect("mi_cuenta")
        return render(request, self.template_name, self.contexto(request, form))


def permiso_denegado(request, exception):
    return render(request, "403.html", status=403)
