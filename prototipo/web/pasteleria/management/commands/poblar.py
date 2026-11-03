"""Carga inicial de usuarios, insumos, catálogo y un pedido de ejemplo."""

from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from pasteleria.menu import CATEGORY_RENAMES, MENU, RENAMES
from pasteleria.models import Cliente, Cotizacion, CotizacionProducto, Insumo, Producto, ProductoInsumo, Usuario, Variante
from pasteleria.reglas import cambiar_estado, convertir_cotizacion


INSUMOS = [
    ("Harina de trigo", 12, 5, "kg"),
    ("Azúcar", 8, 5, "kg"),
    ("Mantequilla", 0.5, 2, "kg"),
    ("Huevos", 30, 10, "un"),
    ("Crema de leche", 1, 4, "L"),
    ("Chocolate cobertura", 8, 5, "kg"),
    ("Manjar", 4, 0.8, "kg"),
    ("Frutilla", 2, 1, "kg"),
]

PRODUCTOS = [
    {
        "nombre": "Torta de Frutillas",
        "descripcion": "Bizcocho de vainilla, crema y frutillas frescas de temporada.",
        "categoria": "Tortas",
        "precio": 25000,
        "disponible": True,
        "imagen_url": "imagenes/torta-frutillas.png",
        "receta": {"Harina de trigo": 0.5, "Azúcar": 0.3, "Huevos": 6, "Frutilla": 0.4, "Crema de leche": 0.3},
    },
    {
        "nombre": "Torta de Chocolate",
        "descripcion": "Bizcocho de chocolate húmedo con relleno de ganache.",
        "categoria": "Tortas",
        "precio": 22000,
        "disponible": True,
        "imagen_url": "imagenes/torta-chocolate.png",
        "receta": {"Harina de trigo": 0.45, "Azúcar": 0.28, "Huevos": 5, "Chocolate cobertura": 0.4},
    },
    {
        "nombre": "Cupcakes",
        "descripcion": "Caja de 6, uno o dos sabores a elección.",
        "categoria": "Cupcakes",
        "precio": 8000,
        "disponible": True,
        "imagen_url": "imagenes/cupcake.png",
        "receta": {"Harina de trigo": 0.08, "Azúcar": 0.06, "Huevos": 1, "Frutilla": 0.05, "Mantequilla": 0.04},
    },
    {
        "nombre": "Cheesecake de Frutos Rojos",
        "descripcion": "Base de galleta, relleno cremoso y salsa de frutos rojos.",
        "categoria": "Tortas",
        "precio": 24000,
        "disponible": False,
        "imagen_url": "",
        "receta": {"Azúcar": 0.2, "Crema de leche": 0.4, "Huevos": 4},
    },
    {
        "nombre": "Galletas de Avena",
        "descripcion": "Galletas artesanales de avena, horneadas al día.",
        "categoria": "Galletas",
        "precio": 6000,
        "disponible": True,
        "imagen_url": "imagenes/galletas-avena.png",
        "receta": {"Harina de trigo": 0.2, "Azúcar": 0.1, "Mantequilla": 0.08},
    },
]


class Command(BaseCommand):
    help = "Puebla la base si está vacía y actualiza el menú."

    def handle(self, *args, **options):
        if Usuario.objects.filter(username="admin").exists():
            self.stdout.write("La base ya tenía datos.")
        else:
            self._cargar_base()
        self._cuenta_con_encargos()
        self._menu_instagram()

    def _cargar_base(self):
        administradora = Usuario.objects.create_user(
            username="admin",
            password=settings.SEED_PASSWORD,
            first_name="María José",
            last_name="Águila",
            rol=Usuario.ADMINISTRADORA,
        )
        Usuario.objects.create_user(
            username="ayudante",
            password=settings.AYUDANTE_PASSWORD,
            first_name="Ayudante",
            last_name="de prueba",
            rol=Usuario.AYUDANTE,
        )

        insumos = {
            nombre: Insumo.objects.create(nombre=nombre, stock_actual=stock, stock_minimo=minimo, unidad_medida=unidad)
            for nombre, stock, minimo, unidad in INSUMOS
        }
        productos = {}
        for item in PRODUCTOS:
            receta = item["receta"]
            producto = Producto.objects.create(
                nombre=item["nombre"],
                descripcion=item["descripcion"],
                categoria=item["categoria"],
                precio=item["precio"],
                disponible=item["disponible"],
                imagen_url=item["imagen_url"],
            )
            for nombre, cantidad in receta.items():
                ProductoInsumo.objects.create(producto=producto, insumo=insumos[nombre], cantidad=cantidad)
            productos[producto.nombre] = producto

        manana = date.today() + timedelta(days=1)
        torta = productos["Torta de Chocolate"]
        cotizacion_cerrada = Cotizacion.objects.create(
            cliente=Cliente.objects.create(nombre="Ana Riquelme", telefono="56911111111", direccion="Pasaje Los Olivos 12"),
            total=torta.precio,
        )
        CotizacionProducto.objects.create(
            cotizacion=cotizacion_cerrada, producto=torta, cantidad=1, precio=torta.precio, subtotal=torta.precio,
        )
        pedido = convertir_cotizacion(cotizacion_cerrada, administradora, manana, 10000, "Retiro")
        cambiar_estado(pedido, "Confirmado")

        cupcake = productos["Cupcakes"]
        abierta = Cotizacion.objects.create(
            cliente=Cliente.objects.create(nombre="Camila Soto", telefono="56987654321"),
            total=cupcake.precio * 2,
        )
        CotizacionProducto.objects.create(
            cotizacion=abierta, producto=cupcake, cantidad=2, precio=cupcake.precio, subtotal=cupcake.precio * 2,
        )
        self.stdout.write(self.style.SUCCESS("Datos de prueba listos. Usuarios: admin y ayudante."))

    def _cuenta_con_encargos(self):
        if Usuario.objects.filter(username="josefina.vera").exists():
            return
        cupcake = Producto.objects.filter(nombre="Cupcakes").first()
        torta = Producto.objects.filter(nombre="Torta de Frutillas").first()
        administradora = Usuario.objects.filter(username="admin").first()
        if cupcake is None or torta is None or administradora is None:
            return
        cuenta = Usuario.objects.create_user(
            username="josefina.vera",
            password=settings.SEED_PASSWORD,
            first_name="Josefina",
            last_name="Vera",
            rol=Usuario.PENDIENTE,
        )
        cliente = Cliente.objects.create(nombre="Josefina Vera", telefono="56974125896", direccion="Bories 850")
        abierta = Cotizacion.objects.create(cliente=cliente, total=cupcake.precio * 3, creada_por=cuenta)
        CotizacionProducto.objects.create(
            cotizacion=abierta, producto=cupcake, cantidad=3, precio=cupcake.precio, subtotal=cupcake.precio * 3,
        )
        cerrada = Cotizacion.objects.create(cliente=cliente, total=torta.precio, creada_por=cuenta)
        CotizacionProducto.objects.create(
            cotizacion=cerrada, producto=torta, cantidad=1, precio=torta.precio, subtotal=torta.precio,
        )
        convertir_cotizacion(cerrada, administradora, date.today() + timedelta(days=2), 10000, "Retiro")
        self.stdout.write(self.style.SUCCESS("Cuenta josefina.vera con una cotización y un pedido."))

    def _menu_instagram(self):
        for viejo, nuevo in RENAMES:
            if not Producto.objects.filter(nombre=nuevo).exists():
                Producto.objects.filter(nombre=viejo).update(nombre=nuevo)
        for viejo, nuevo in CATEGORY_RENAMES:
            Producto.objects.filter(categoria=viejo).update(categoria=nuevo)
        Producto.objects.filter(nombre__in=["Rollos de pizza (tomate, queso y orégano)", "Rollo de ajo"]).update(
            categoria="Rollitos salados"
        )
        opciones_menu = {
            "Alfajor brownie manjar": "Relleno:manjar café,manjar menta,manjar limón,manjar chocolate,manjar frambuesa",
            "Berlines": "Sabor:manjar,crema pastelera,membrillo,chocolate",
            "Mini rollos sabor": "Sabor:pie de limón,Oreo,tiramisú,frambuesa,manjar,canela manzana",
            "Cupcakes": "Sabor:chocolate con menta,vainilla frutilla,vainilla bariloche,vainilla manjar plátano",
            "Mini berlín (pastelera, membrillo o chocolate)": "Sabor:crema pastelera,membrillo,chocolate",
        }
        for item in MENU:
            producto, _ = Producto.objects.update_or_create(
                nombre=item["nombre"],
                defaults={
                    "descripcion": item["descripcion"],
                    "categoria": item["categoria"],
                    "precio": item["precio"],
                    "disponible": True,
                    "imagen_url": item.get("imagen_url", ""),
                    "opciones": opciones_menu.get(item["nombre"], ""),
                },
            )
            formatos = []
            for orden, (formato, precio) in enumerate(item.get("variantes", [])):
                Variante.objects.update_or_create(
                    producto=producto,
                    formato=formato,
                    defaults={"precio": precio, "orden": orden},
                )
                formatos.append(formato)
            producto.variantes.exclude(formato__in=formatos).delete()
        vigentes = {item["nombre"] for item in MENU}
        sobrantes = Producto.objects.exclude(nombre__in=vigentes)
        for producto in sobrantes:
            try:
                producto.delete()
            except Exception:
                producto.disponible = False
                producto.save(update_fields=["disponible"])
        Producto.objects.update(agotado=False)
        destacado = Producto.objects.filter(nombre="Pie de limón", disponible=True).first()
        if destacado:
            destacado.agotado = True
            destacado.save(update_fields=["agotado"])
        self.stdout.write(self.style.SUCCESS("Catálogo 2026 actualizado."))
