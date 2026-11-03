"""Modelos de la pastelería: usuarios, catálogo, cotizaciones y pedidos."""

from datetime import date, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.templatetags.static import static


class Usuario(AbstractUser):
    """Cuenta del equipo o cliente registrado."""
    ADMINISTRADORA = "administradora"
    AYUDANTE = "ayudante"
    PENDIENTE = "pendiente"
    ROLES = [
        (ADMINISTRADORA, "Administradora"),
        (AYUDANTE, "Ayudante"),
        (PENDIENTE, "Pendiente de habilitación"),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default=PENDIENTE)
    debe_cambiar_clave = models.BooleanField(
        default=False,
        help_text="Clave provisoria: hay que cambiarla al entrar.",
    )

    class Meta:
        verbose_name = "usuario"
        indexes = [models.Index(fields=["rol"])]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def es_administradora(self):
        return self.rol == self.ADMINISTRADORA

    @property
    def entra_al_panel(self):
        return self.rol in (self.ADMINISTRADORA, self.AYUDANTE)


class Cliente(models.Model):
    nombre = models.CharField(max_length=80)
    telefono = models.CharField(max_length=20, unique=True)
    direccion = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.telefono})"


class Insumo(models.Model):
    UNIDADES = [("kg", "kg"), ("g", "g"), ("L", "L"), ("un", "un")]
    nombre = models.CharField(max_length=80, unique=True)
    stock_actual = models.FloatField(default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.FloatField(default=0, validators=[MinValueValidator(0)])
    unidad_medida = models.CharField(max_length=10, choices=UNIDADES)

    class Meta:
        ordering = ["nombre"]
        constraints = [
            models.CheckConstraint(check=models.Q(stock_actual__gte=0), name="insumo_stock_no_negativo"),
        ]

    def __str__(self):
        return self.nombre

    @property
    def requiere_reposicion(self):
        return self.stock_actual <= self.stock_minimo


class Producto(models.Model):
    CATEGORIAS = [
        ("Rollitos dulces", "Dulces"),
        ("Rollitos salados", "Salados"),
        ("Alfajores sabores", "Sabores"),
        ("Alfajores veganos", "Veganos"),
        ("Bombitas", "Bombitas"),
        ("Productos mini", "Productos mini"),
        ("Berlines", "Berlines"),
        ("Untables", "Untables"),
        ("Queques", "Queques"),
        ("Cupcakes", "Cupcakes"),
        ("Tortas", "Tortas"),
        ("Tartas", "Tartas"),
        ("Pies", "Pies"),
        ("Porciones", "Porciones"),
        ("Día de la madre", "Día de la madre"),
        ("Día del padre", "Día del padre"),
        ("Día de Pascua", "Día de Pascua"),
        ("Fiestas patrias", "Fiestas patrias"),
    ]
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=240, blank=True)
    categoria = models.CharField(max_length=40, choices=CATEGORIAS, default="Tortas")
    precio = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    imagen = models.ImageField(upload_to="productos/", blank=True)
    imagen_url = models.CharField(max_length=400, blank=True)
    opciones = models.CharField(
        max_length=300,
        blank=True,
        help_text="Ejemplo: Relleno:café,menta,limón,chocolate,frambuesa",
    )
    disponible = models.BooleanField(default=True)
    agotado = models.BooleanField(default=False, help_text="Marca Sin stock en el catálogo.")

    class Meta:
        ordering = ["nombre"]
        indexes = [models.Index(fields=["categoria", "disponible"])]
        constraints = [
            models.CheckConstraint(check=models.Q(precio__gt=0), name="producto_precio_positivo"),
        ]

    def __str__(self):
        return self.nombre

    @property
    def fotos(self):
        if self.imagen:
            return [self.imagen.url]
        return [static(ruta.strip()) for ruta in self.imagen_url.split(",") if ruta.strip()]

    def url_foto(self):
        album = self.fotos
        return album[0] if album else ""

    def alcanza_para(self, unidades):
        if not self.disponible or self.agotado:
            return False
        return all(item.insumo.stock_actual >= item.cantidad * unidades for item in self.receta.all())

    @property
    def sin_stock(self):
        return self.agotado or not self.alcanza_para(1)

    def lista_opciones(self):
        texto = (self.opciones or "").strip()
        if not texto or ":" not in texto:
            return None
        etiqueta, resto = texto.split(":", 1)
        elecciones = [parte.strip() for parte in resto.split(",") if parte.strip()]
        if not elecciones:
            return None
        return {"etiqueta": etiqueta.strip(), "elecciones": elecciones}


class ProductoInsumo(models.Model):
    producto = models.ForeignKey(Producto, related_name="receta", on_delete=models.CASCADE)
    insumo = models.ForeignKey(Insumo, related_name="usado_en", on_delete=models.PROTECT)
    cantidad = models.FloatField(validators=[MinValueValidator(0.001)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["producto", "insumo"], name="receta_sin_insumo_repetido"),
        ]

    def __str__(self):
        return f"{self.cantidad:g} {self.insumo.unidad_medida} de {self.insumo} en {self.producto}"


class Variante(models.Model):
    producto = models.ForeignKey(Producto, related_name="variantes", on_delete=models.CASCADE)
    formato = models.CharField(max_length=80)
    precio = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden", "id"]
        constraints = [
            models.UniqueConstraint(fields=["producto", "formato"], name="variante_formato_unico"),
            models.CheckConstraint(check=models.Q(precio__gt=0), name="variante_precio_positivo"),
        ]

    def __str__(self):
        return f"{self.formato} ({self.producto})"


class Cotizacion(models.Model):
    ENVIADA = "Enviada"
    CONVERTIDA = "Convertida"
    ESTADOS = [(ENVIADA, ENVIADA), (CONVERTIDA, CONVERTIDA)]
    cliente = models.ForeignKey(Cliente, related_name="cotizaciones", on_delete=models.PROTECT)
    creada_por = models.ForeignKey(
        Usuario, related_name="cotizaciones", null=True, blank=True, on_delete=models.SET_NULL,
    )
    fecha = models.DateField(default=date.today)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ENVIADA)
    total = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-fecha", "-id"]
        indexes = [models.Index(fields=["estado"])]

    def __str__(self):
        return f"Cotización {self.pk}"

    @property
    def clase_estado(self):
        return self.estado.lower()


class CotizacionProducto(models.Model):
    cotizacion = models.ForeignKey(Cotizacion, related_name="lineas", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name="lineas_cotizacion", on_delete=models.PROTECT)
    formato = models.CharField(max_length=80, blank=True, default="")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class PedidoQuerySet(models.QuerySet):
    def vigentes(self):
        return self.exclude(estado="Cancelado")

    def con_detalle(self):
        return self.select_related("cotizacion__cliente", "registrado_por").prefetch_related(
            "lineas__producto"
        )


class Pedido(models.Model):
    PENDIENTE = "Pendiente"
    CONFIRMADO = "Confirmado"
    EN_PREPARACION = "En preparación"
    LISTO = "Listo"
    ENTREGADO = "Entregado"
    CANCELADO = "Cancelado"
    ESTADOS = [
        (PENDIENTE, PENDIENTE),
        (CONFIRMADO, CONFIRMADO),
        (EN_PREPARACION, EN_PREPARACION),
        (LISTO, LISTO),
        (ENTREGADO, ENTREGADO),
        (CANCELADO, CANCELADO),
    ]
    TRANSICIONES = {
        PENDIENTE: (CONFIRMADO, CANCELADO),
        CONFIRMADO: (EN_PREPARACION, CANCELADO),
        EN_PREPARACION: (LISTO,),
        LISTO: (ENTREGADO,),
        ENTREGADO: (),
        CANCELADO: (),
    }
    CANALES = [("Retiro", "Retiro"), ("Despacho", "Despacho")]

    cotizacion = models.OneToOneField(Cotizacion, related_name="pedido", on_delete=models.PROTECT)
    registrado_por = models.ForeignKey(Usuario, related_name="pedidos", on_delete=models.PROTECT)
    fecha_pedido = models.DateField(default=date.today)
    fecha_entrega = models.DateField()
    monto_total = models.PositiveIntegerField()
    abono = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)
    canal_despacho = models.CharField(max_length=10, choices=CANALES)
    stock_descontado = models.BooleanField(default=False)

    objects = PedidoQuerySet.as_manager()

    class Meta:
        ordering = ["-fecha_pedido", "-id"]
        indexes = [
            models.Index(fields=["estado"]),
            models.Index(fields=["fecha_entrega"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(abono__lte=models.F("monto_total")), name="pedido_abono_no_supera_total"),
        ]

    def __str__(self):
        return f"Pedido {self.pk}"

    def clean(self):
        if self.abono is not None and self.monto_total is not None and self.abono > self.monto_total:
            raise ValidationError({"abono": "El abono no puede superar el total."})
        if self.fecha_entrega:
            hoy = date.today()
            if self.fecha_entrega < hoy and not self.pk:
                raise ValidationError({"fecha_entrega": "La fecha de entrega no puede ser anterior a hoy."})
            if self.fecha_entrega > hoy + timedelta(days=365):
                raise ValidationError({"fecha_entrega": "La entrega no puede ser a más de un año desde hoy."})

    @property
    def saldo(self):
        return self.monto_total - self.abono

    @property
    def siguientes_estados(self):
        return list(self.TRANSICIONES[self.estado])

    @property
    def clase_estado(self):
        return self.estado.lower().replace(" ", "-")


class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="lineas", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, related_name="lineas_pedido", on_delete=models.PROTECT)
    formato = models.CharField(max_length=80, blank=True, default="")
    cantidad = models.PositiveIntegerField()
    precio = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


class CompraInsumo(models.Model):
    insumo = models.ForeignKey(Insumo, related_name="compras", on_delete=models.PROTECT)
    nombre = models.CharField(max_length=80)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    proveedor = models.CharField(max_length=80)
    precio_compra = models.PositiveIntegerField()
    cantidad_comprada = models.FloatField(validators=[MinValueValidator(0.001)])

    class Meta:
        ordering = ["fecha_vencimiento", "-id"]

    def __str__(self):
        return f"{self.nombre} ({self.proveedor})"

    def esta_por_vencer(self, dias=3):
        if self.fecha_vencimiento is None:
            return False
        return date.today() <= self.fecha_vencimiento <= date.today() + timedelta(days=dias)
