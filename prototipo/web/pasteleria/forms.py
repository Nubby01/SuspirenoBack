"""Formularios del sitio público y del panel."""

import re
from datetime import date, timedelta

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm

from .models import Cliente, CompraInsumo, Insumo, Pedido, Producto, ProductoInsumo, Usuario

TELEFONO = re.compile(r"^\+?\d{8,15}$")
TOPE_IMAGEN = 2 * 1024 * 1024
ENTREGA_MAX_DIAS = 365


def _rango_entrega():
    """Hoy y tope de un año para la fecha de entrega."""
    hoy = date.today()
    return hoy, hoy + timedelta(days=ENTREGA_MAX_DIAS)


def widget_fecha_entrega():
    """Input date con min y max."""
    minimo, maximo = _rango_entrega()
    return forms.DateInput(attrs={
        "type": "date",
        "min": minimo.isoformat(),
        "max": maximo.isoformat(),
    })


def validar_fecha_entrega(valor):
    """Revisa que la entrega esté entre hoy y un año."""
    minimo, maximo = _rango_entrega()
    if valor < minimo:
        raise forms.ValidationError("La fecha de entrega no puede ser anterior a hoy.")
    if valor > maximo:
        raise forms.ValidationError("La entrega no puede ser a más de un año desde hoy.")
    return valor


def convertir_cantidad(cantidad, desde, hacia):
    """Pasa entre kg/g o L/ml cuando hace falta."""
    if desde == hacia:
        return cantidad
    if desde == "kg" and hacia == "g":
        return cantidad * 1000
    if desde == "g" and hacia == "kg":
        return cantidad / 1000
    raise forms.ValidationError(
        f"No se puede pasar de {desde} a {hacia}. Usa la misma familia de medida del insumo ({hacia})."
    )


class IngresoForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Ese nombre de usuario o esa clave no coinciden.",
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].help_text = ""
        self.fields["username"].widget.attrs.update({
            "autocomplete": "username",
            "placeholder": "josefina.vera",
        })
        self.fields["password"].label = "Clave"
        self.fields["password"].help_text = ""
        self.fields["password"].widget.attrs.update({"autocomplete": "current-password"})


class RegistroForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": "Las dos claves no coinciden.",
    }
    nombre = forms.CharField(
        max_length=80,
        label="Tu nombre",
        help_text="",
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["nombre"].widget.attrs.update({"autocomplete": "name", "placeholder": "Josefina Vera"})
        self.fields["username"].label = "Nombre de usuario"
        self.fields["username"].help_text = ""
        self.fields["username"].widget.attrs.update({"autocomplete": "username", "placeholder": "josefina.vera"})
        self.fields["password1"].label = "Clave"
        self.fields["password1"].help_text = ""
        self.fields["password1"].widget.attrs.update({"autocomplete": "new-password"})
        self.fields["password2"].label = "Repite la clave"
        self.fields["password2"].help_text = ""
        self.fields["password2"].widget.attrs.update({"autocomplete": "new-password"})

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("Escribe tu nombre completo.")
        return nombre

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if " " in username:
            raise forms.ValidationError("El nombre de usuario no puede tener espacios.")
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.first_name = self.cleaned_data["nombre"]
        usuario.rol = Usuario.PENDIENTE
        if commit:
            usuario.save()
        return usuario


class CambiarClaveForm(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "La clave actual no coincide. Escríbela otra vez.",
        "password_mismatch": "Las dos claves nuevas no coinciden.",
    }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.obligar = bool(getattr(self.user, "debe_cambiar_clave", False))
        self.fields["old_password"].label = "Clave provisoria" if self.obligar else "Clave actual"
        self.fields["old_password"].help_text = ""
        self.fields["old_password"].widget.attrs.update({"autocomplete": "current-password"})
        self.fields["new_password1"].label = "Nueva clave"
        self.fields["new_password1"].help_text = ""
        self.fields["new_password1"].required = self.obligar
        self.fields["new_password1"].widget.attrs.update({"autocomplete": "new-password"})
        self.fields["new_password2"].label = "Repite la nueva clave"
        self.fields["new_password2"].help_text = ""
        self.fields["new_password2"].required = self.obligar
        self.fields["new_password2"].widget.attrs.update({"autocomplete": "new-password"})

    def clean(self):
        nueva = self.cleaned_data.get("new_password1")
        repetida = self.cleaned_data.get("new_password2")
        if self.obligar and (not nueva or not repetida):
            raise forms.ValidationError("Debes elegir una clave nueva para seguir.")
        if not nueva and not repetida:
            return self.cleaned_data
        if not nueva or not repetida:
            raise forms.ValidationError("Escribe la clave nueva dos veces, iguales.")
        self.validate_passwords("new_password1", "new_password2")
        self.validate_password_for_user(self.user, "new_password2")
        return self.cleaned_data

    def save(self, commit=True):
        if not self.cleaned_data.get("new_password1"):
            return self.user
        usuario = super().save(commit=False)
        usuario.debe_cambiar_clave = False
        if commit:
            usuario.save()
        return usuario


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ("nombre", "descripcion", "categoria", "precio", "imagen", "imagen_url", "opciones", "disponible", "agotado")
        labels = {
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "precio": "Precio",
            "imagen": "Foto (opcional, máx. 2 MB)",
            "imagen_url": "Ruta de imagen estática",
            "opciones": "Opciones a elegir (Relleno:café,menta)",
            "disponible": "Disponible en el catálogo",
            "agotado": "Marcar sin stock",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 5}),
            "disponible": forms.CheckboxInput(attrs={"class": "check-grande"}),
            "agotado": forms.CheckboxInput(attrs={"class": "check-grande"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["precio"].error_messages["min_value"] = "El precio debe ser mayor que cero."

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if imagen and getattr(imagen, "size", 0) > TOPE_IMAGEN:
            raise forms.ValidationError("La imagen no puede pesar más de 2 MB.")
        return imagen


class RecetaForm(forms.ModelForm):
    unidad = forms.ChoiceField(choices=Insumo.UNIDADES, label="Unidad de medida")

    class Meta:
        model = ProductoInsumo
        fields = ("insumo", "cantidad")
        labels = {"cantidad": "Cantidad"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cantidad"].widget.attrs.update({"step": "any", "min": "0", "placeholder": "Ej: 0.5"})
        if self.is_bound:
            return
        primero = self.fields["insumo"].queryset.first()
        if primero:
            self.fields["unidad"].initial = primero.unidad_medida

    def clean(self):
        limpio = super().clean()
        insumo = limpio.get("insumo")
        cantidad = limpio.get("cantidad")
        unidad = limpio.get("unidad")
        if insumo is None or cantidad is None or not unidad:
            return limpio
        try:
            limpio["cantidad"] = convertir_cantidad(cantidad, unidad, insumo.unidad_medida)
        except forms.ValidationError as error:
            self.add_error("unidad", error)
        return limpio


class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ("nombre", "stock_actual", "stock_minimo", "unidad_medida")
        labels = {
            "stock_actual": "Stock actual",
            "stock_minimo": "Stock mínimo",
            "unidad_medida": "Unidad (kg, g, L o un)",
        }
        help_texts = {
            "stock_actual": "Cantidad disponible en la unidad elegida abajo.",
            "stock_minimo": "Alerta cuando el stock baje de este valor, en la misma unidad.",
        }


class CompraForm(forms.ModelForm):
    class Meta:
        model = CompraInsumo
        fields = ("nombre", "proveedor", "precio_compra", "cantidad_comprada", "fecha_vencimiento")
        labels = {
            "nombre": "Qué se compró",
            "precio_compra": "Precio de compra",
            "cantidad_comprada": "Cantidad",
            "fecha_vencimiento": "Vencimiento",
        }
        widgets = {"fecha_vencimiento": forms.DateInput(attrs={"type": "date"})}


class CotizacionClienteForm(forms.Form):
    nombre = forms.CharField(
        max_length=80,
        label="Tu nombre",
        widget=forms.TextInput(attrs={"autocomplete": "name", "placeholder": "Josefina Vera"}),
        error_messages={"required": "Escribe tu nombre."},
    )
    telefono = forms.CharField(
        max_length=20,
        label="Teléfono",
        widget=forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "56974125896", "inputmode": "tel"}),
        error_messages={"required": "Escribe un teléfono de contacto."},
    )
    direccion = forms.CharField(
        max_length=160,
        required=False,
        label="Dirección",
        widget=forms.TextInput(attrs={"autocomplete": "street-address", "placeholder": "Bories 850"}),
    )

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("Escribe tu nombre completo.")
        return nombre

    def clean_telefono(self):
        telefono = re.sub(r"[\s-]", "", self.cleaned_data["telefono"])
        if not TELEFONO.match(telefono):
            raise forms.ValidationError("El teléfono debe tener entre 8 y 15 dígitos.")
        return telefono


class ConvertirPedidoForm(forms.Form):
    fecha_entrega = forms.DateField(label="Fecha de entrega", widget=widget_fecha_entrega())
    abono = forms.IntegerField(min_value=0, label="Abono")
    canal_despacho = forms.ChoiceField(choices=Pedido.CANALES, label="Entrega")

    def clean_fecha_entrega(self):
        return validar_fecha_entrega(self.cleaned_data["fecha_entrega"])


class CotizacionEditarForm(forms.Form):
    nombre = forms.CharField(max_length=80, label="Cliente")
    telefono = forms.CharField(max_length=20, label="Teléfono")
    direccion = forms.CharField(max_length=160, required=False, label="Dirección")

    def __init__(self, *args, cotizacion=None, **kwargs):
        self.cotizacion = cotizacion
        super().__init__(*args, **kwargs)
        if cotizacion and not self.is_bound:
            cliente = cotizacion.cliente
            self.fields["nombre"].initial = cliente.nombre
            self.fields["telefono"].initial = cliente.telefono
            self.fields["direccion"].initial = cliente.direccion

    def clean_telefono(self):
        telefono = re.sub(r"[\s-]", "", self.cleaned_data["telefono"])
        if not TELEFONO.match(telefono):
            raise forms.ValidationError("El teléfono debe tener entre 8 y 15 dígitos.")
        conflicto = Cliente.objects.filter(telefono=telefono)
        if self.cotizacion:
            conflicto = conflicto.exclude(pk=self.cotizacion.cliente_id)
        if conflicto.exists():
            raise forms.ValidationError("Ese teléfono ya está en otra cuenta de cliente.")
        return telefono

    def save(self):
        cliente = self.cotizacion.cliente
        cliente.nombre = self.cleaned_data["nombre"].strip()
        cliente.telefono = self.cleaned_data["telefono"]
        cliente.direccion = self.cleaned_data.get("direccion", "").strip()
        cliente.save()
        return self.cotizacion


class PedidoManualForm(forms.Form):
    nombre = forms.CharField(max_length=80, label="Cliente")
    telefono = forms.CharField(max_length=20, label="Teléfono")
    direccion = forms.CharField(max_length=160, required=False, label="Dirección")
    producto = forms.ModelChoiceField(queryset=Producto.objects.filter(disponible=True).order_by("nombre"), label="Producto")
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad")
    formato = forms.CharField(
        max_length=80,
        required=False,
        label="Tamaño o sabor",
        help_text="Solo si aplica: por ejemplo 15 personas, manjar o vainilla. Si no, déjalo vacío.",
    )
    fecha_entrega = forms.DateField(label="Fecha de entrega", widget=widget_fecha_entrega())
    abono = forms.IntegerField(min_value=0, initial=0, label="Abono")
    canal_despacho = forms.ChoiceField(choices=Pedido.CANALES, label="Entrega")
    estado = forms.ChoiceField(choices=Pedido.ESTADOS, initial=Pedido.PENDIENTE, label="Estado")

    def clean_telefono(self):
        telefono = re.sub(r"[\s-]", "", self.cleaned_data["telefono"])
        if not TELEFONO.match(telefono):
            raise forms.ValidationError("El teléfono debe tener entre 8 y 15 dígitos.")
        return telefono

    def clean_fecha_entrega(self):
        return validar_fecha_entrega(self.cleaned_data["fecha_entrega"])


class PedidoEditarForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ("fecha_entrega", "abono", "canal_despacho", "estado")
        widgets = {"fecha_entrega": widget_fecha_entrega()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fecha_entrega"].widget = widget_fecha_entrega()

    def clean_fecha_entrega(self):
        return validar_fecha_entrega(self.cleaned_data["fecha_entrega"])


class AyudanteForm(forms.Form):
    nombre = forms.CharField(max_length=80, label="Nombre")
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    password1 = forms.CharField(
        label="Clave provisoria",
        widget=forms.PasswordInput,
        help_text="Cuenta provisoria: el ayudante deberá cambiar esta clave al ingresar por primera vez.",
    )
    password2 = forms.CharField(label="Repite la clave provisoria", widget=forms.PasswordInput)
    clave_admin = forms.CharField(
        label="Tu clave de administradora",
        widget=forms.PasswordInput,
        help_text="Confirma con tu clave para crear la cuenta del equipo.",
    )

    def __init__(self, *args, admin=None, **kwargs):
        self.admin = admin
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if " " in username:
            raise forms.ValidationError("El nombre de usuario no puede tener espacios.")
        if Usuario.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username

    def clean(self):
        limpio = super().clean()
        if limpio.get("password1") != limpio.get("password2"):
            self.add_error("password2", "Las dos claves no coinciden.")
        if self.admin and limpio.get("clave_admin") and not self.admin.check_password(limpio["clave_admin"]):
            self.add_error("clave_admin", "La clave de administradora no coincide.")
        return limpio


class AyudanteEditarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo",
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if " " in username:
            raise forms.ValidationError("El nombre de usuario no puede tener espacios.")
        conflicto = Usuario.objects.filter(username__iexact=username).exclude(pk=self.instance.pk)
        if conflicto.exists():
            raise forms.ValidationError("Ese nombre de usuario ya está en uso.")
        return username
