"""Datos del menú y del banner para poblar el catálogo."""

RENAMES = [
    ("Rollitos de canela", "Rollos de canela"),
    ("Rollitos de limón", "Rollo sabor pie de limón"),
    ("Rollitos de pizza", "Rollos de pizza (tomate, queso y orégano)"),
    ("Rollos de frambuesa", "Rollo sabor frambuesa"),
    ("Alfajor de maicena", "Alfajor de maicena"),
    ("Alfajores de maicena", "Alfajor de maicena"),
    ("Cupcake de Frutilla", "Cupcakes"),
]

CATEGORY_RENAMES = [
    ("Rollitos tradicionales", "Rollitos dulces"),
    ("Rollitos de canela sabores", "Rollitos dulces"),
    ("Alfajores artesanales", "Alfajores sabores"),
]

TORTA_GALLETA = (
    ("10 personas", 15000),
    ("15 personas", 20000),
    ("20 personas", 25000),
    ("25 personas", 28000),
    ("30 personas", 32000),
)
TORTA_BIZCOCHO = (
    ("10 personas", 24000),
    ("15 personas", 30000),
    ("20 personas", 32000),
    ("25 personas", 35000),
    ("30 personas", 40000),
)
TORTA_AMOR = (
    ("10 personas", 28000),
    ("15 personas", 35000),
    ("20 personas", 38000),
    ("25 personas", 45000),
    ("30 personas", 50000),
)
TORTA_FESTIVA = (
    ("Galleta · 10 personas", 15000),
    ("Galleta · 15 personas", 20000),
    ("Bizcocho · 10 personas", 24000),
    ("Bizcocho · 15 personas", 30000),
)

UNIDAD = "Precio por unidad."
CUATRO = "Bandeja de 4 unidades."
SABOR_ROLLO = "Bandeja de 4. Hasta dos sabores al pedir."

# Orden de pestañas en el catálogo
GRUPOS_NAV = [
    {
        "etiqueta": "Rollitos",
        "hijos": [
            ("Rollitos dulces", "Dulces"),
            ("Rollitos salados", "Salados"),
        ],
    },
    {
        "etiqueta": "Alfajores",
        "hijos": [
            ("Alfajores sabores", "Sabores"),
            ("Alfajores veganos", "Veganos"),
        ],
    },
    {
        "etiqueta": "Tortas y tartas",
        "hijos": [
            ("Tortas", "Tortas"),
            ("Tartas", "Tartas"),
            ("Pies", "Pies"),
            ("Porciones", "Porciones"),
        ],
    },
    {
        "etiqueta": "Festividades",
        "hijos": [
            ("Día de la madre", "Madre"),
            ("Día del padre", "Padre"),
            ("Día de Pascua", "Pascua"),
            ("Fiestas patrias", "Fiestas patrias"),
        ],
    },
    {
        "etiqueta": "Más",
        "hijos": [
            ("Bombitas", "Bombitas"),
            ("Productos mini", "Mini"),
            ("Berlines", "Berlines"),
            ("Untables", "Untables"),
            ("Queques", "Queques"),
            ("Cupcakes", "Cupcakes"),
        ],
    },
]

FESTIVAS = {
    "Día de la madre",
    "Día del padre",
    "Día de Pascua",
    "Fiestas patrias",
}

BANNER = [
    "imagenes/tortas-10-personas.png",
    "imagenes/alfajor-brownie-manjar.png",
    "imagenes/pie-limon.png",
    "imagenes/rollo-canela.png",
    "imagenes/tortaamor.png",
]


def _item(nombre, descripcion, categoria, precio, imagen="", variantes=None):
    if isinstance(imagen, (list, tuple)):
        imagen = ",".join(imagen)
    dato = {
        "nombre": nombre,
        "descripcion": descripcion,
        "categoria": categoria,
        "precio": precio,
        "imagen_url": imagen,
    }
    if variantes:
        dato["variantes"] = list(variantes)
        dato["precio"] = min(valor for _, valor in variantes)
    return dato


MENU = [
    _item("Rollos de canela", CUATRO, "Rollitos dulces", 8500, "imagenes/rollo-canela.png"),
    _item("Rollo sabor pie de limón", SABOR_ROLLO, "Rollitos dulces", 10500, "imagenes/rollo-pie-limon.png"),
    _item("Rollo sabor Oreo", SABOR_ROLLO, "Rollitos dulces", 10500, "imagenes/rollo-oreo.png"),
    _item("Rollo sabor tiramisú", SABOR_ROLLO, "Rollitos dulces", 10500, "imagenes/rollo-tiramisu.png"),
    _item("Rollo sabor frambuesa", SABOR_ROLLO, "Rollitos dulces", 10500, "imagenes/rollo-frambuesa.png"),
    _item("Rollo sabor manjar", SABOR_ROLLO, "Rollitos dulces", 10500, "imagenes/rollo-manjar.png"),
    _item("Rollo sabor canela manzana", SABOR_ROLLO, "Rollitos dulces", 10500, "imagenes/rollo-canela-manzana.png"),
    _item(
        "Rollos de pizza (tomate, queso y orégano)",
        "Salsa de tomate, queso y orégano. Bandeja de 4.",
        "Rollitos salados",
        10500,
        "imagenes/rollo-pizza.png",
    ),
    _item("Rollo de ajo", SABOR_ROLLO, "Rollitos salados", 10500, "imagenes/rollo-ajo.png"),
    _item("Alfajor choco maní", f"{UNIDAD} Baño blanco o semiamargo, con maní encima.", "Alfajores sabores", 1700, "imagenes/alfajor-choco-mani.png"),
    _item("Alfajor choco maní con frambuesa", f"{UNIDAD} Centro de frambuesa.", "Alfajores sabores", 1800, "imagenes/alfajor-choco-mani-frambuesa.png"),
    _item("Alfajor de manjar", f"{UNIDAD} Tapas de cacao, relleno de manjar y baño de chocolate.", "Alfajores sabores", 1700, "imagenes/alfajor-manjar.png"),
    _item(
        "Alfajor de manjar con frambuesa",
        f"{UNIDAD} Centro de frambuesa o frutos rojos.",
        "Alfajores sabores",
        1800,
        "imagenes/alfajormanjarframbuesa.png",
    ),
    _item("Alfajor de pistacho", UNIDAD, "Alfajores sabores", 2400, "imagenes/alfajordepistacho.png"),
    _item("Alfajor ganache y naranjitas", UNIDAD, "Alfajores sabores", 1800, "imagenes/aolfajorconnaranjitas.png"),
    _item("Alfajor ganache cookies & cream", UNIDAD, "Alfajores sabores", 2000, "imagenes/alfajordeganachedecookiesandcream.png"),
    _item("Alfajor choco avellana crunchy", UNIDAD, "Alfajores sabores", 2400, "imagenes/alfajor-choco-avellana-crunchy.png"),
    _item("Alfajor manjar y crema de avellanas", UNIDAD, "Alfajores sabores", 2000, "imagenes/alfajormanjarycremadeavellanas.png"),
    _item("Alfajor pasta de maní", f"{UNIDAD} Pasta de maní con baño de chocolate.", "Alfajores sabores", 1800, "imagenes/alfajor-pasta-mani.png"),
    _item(
        "Alfajor brownie manjar",
        f"{UNIDAD} Centro a elección.",
        "Alfajores sabores",
        2400,
        ["imagenes/alfajor-brownie-manjar.png", "imagenes/alfajor-brownie-limon.png"],
    ),
    _item("Alfajor de maicena", "Caja de 4. Rellenos de manjar y cubiertos de coco rallado.", "Alfajores sabores", 6000, "imagenes/alfajor-maicena.png"),
    _item("Alfajor cheesecake", f"{UNIDAD} Sabor a elección: frutos rojos, limón o maracuyá.", "Alfajores sabores", 2000, "imagenes/alfajor-cheesecake.png"),
    _item("Alfajor manjaracuyá", UNIDAD, "Alfajores sabores", 1800, "imagenes/alfajormaracuya.png"),
    _item("Alfajor de membrillo", UNIDAD, "Alfajores sabores", 1700, "imagenes/alfajormenbrillo.png"),
    _item("Alfajor choco maní vegano", f"{UNIDAD} Baño de chocolate semiamargo.", "Alfajores veganos", 1700, "imagenes/alfajor-choco-mani.png"),
    _item("Alfajor choco maní con frambuesa vegano", f"{UNIDAD} Baño de chocolate semiamargo y centro de frambuesa.", "Alfajores veganos", 1800, "imagenes/alfajor-choco-mani-frambuesa.png"),
    _item("Bombita brownie manjar, bañada en chocolate", "Caja de 6. Cada una pesa cerca de 30 g.", "Bombitas", 5000, "imagenes/bombita-brownie-manjar.png"),
    _item("Bombita vainilla manjar, bañada en chocolate", "Caja de 6. Cada una pesa cerca de 30 g.", "Bombitas", 5000, "imagenes/bombita-vainilla-manjar.png"),
    _item("Bombita Oreo queso crema, bañada en chocolate", "Caja de 6. Cada una pesa cerca de 30 g.", "Bombitas", 6000, "imagenes/bombita-oreo.png"),
    _item("Bombita Tritón manjar, bañada en chocolate", "Caja de 6. Cada una pesa cerca de 30 g.", "Bombitas", 5000, "imagenes/bombita-triton-manjar.png"),
    _item("Mini alfajores de manjar", "Caja de 20 unidades.", "Productos mini", 15000, "imagenes/alfajor-manjar.png"),
    _item("Mini alfajores de maicena", "Caja de 20 unidades.", "Productos mini", 12000, "imagenes/alfajor-maicena.png"),
    _item("Mini rollos de canela", "Caja de 12 unidades.", "Productos mini", 13000, "imagenes/rollo-canela.png"),
    _item("Mini rollos sabor", "Caja de 12 unidades. El sabor se indica al pedir.", "Productos mini", 15000, "imagenes/mini-rollo-sabor.png"),
    _item("Mini berlín (pastelera, membrillo o chocolate)", "Caja de 20 unidades.", "Productos mini", 15000, "imagenes/berlines.png"),
    _item("Berlines", "Caja de 4. Sabores: manjar, crema pastelera, membrillo o chocolate. Hasta dos sabores.", "Berlines", 5000, "imagenes/berlines.png"),
    _item("Mantequilla de maní", "Frasco de 450 g, tradicional.", "Untables", 5500, "imagenes/mantequilla-mani.png"),
    _item("Mantequilla de maní cacao", "Frasco de 450 g, mantequilla de maní con cacao.", "Untables", 6000, "imagenes/mantequilla-cacao.png"),
    _item("Mantequilla de maní con chips", "Frasco de 450 g, con chips de chocolate.", "Untables", 6000, "imagenes/mantequilla-chips.png"),
    _item(
        "Torta de galleta (crema, manjar y plátano)",
        "Galletas de vainilla con crema, manjar y plátano.",
        "Tortas",
        15000,
        ["imagenes/tortadegalletas.png", "imagenes/porcion-torta-galleta.png"],
        TORTA_GALLETA,
    ),
    _item(
        "Torta de bizcocho",
        "Vainilla o chocolate, con hasta 2 rellenos a elección.",
        "Tortas",
        24000,
        ["imagenes/torta-chocolate.png", "imagenes/torta-frutillas.png"],
        TORTA_BIZCOCHO,
    ),
    _item(
        "Torta mixta (bizcocho y hoja)",
        "Bizcocho de chocolate y hoja, con crema, manjar y frutillas.",
        "Tortas",
        24000,
        "imagenes/tortamixta.png",
        TORTA_BIZCOCHO,
    ),
    _item(
        "Torta amor",
        "Hojarasca con crema pastelera, manjar y crema con frambuesas.",
        "Tortas",
        28000,
        ["imagenes/tortaamor.png", "imagenes/porcion-torta-amor.png"],
        TORTA_AMOR,
    ),
    _item("Torta de yogurt", "Base de bizcocho, relleno de yogurt y cubierta de gelatina. Para 15 personas.", "Tortas", 18000, ["imagenes/torta-yogurt.png", "imagenes/porcion-torta-yogurt.png"]),
    _item("Pie de limón", "Pie entero, con merengue flameado.", "Pies", 13000, ["imagenes/pie-limon.png", "imagenes/porcion-pie-limon.png"]),
    _item("Pie de frambuesa", "Pie entero.", "Pies", 16000, ["imagenes/pie-frambuesa.png", "imagenes/porcion-pie-frambuesa.png"]),
    _item("Pie de maracuyá", "Pie entero.", "Pies", 16000, "imagenes/pie-maracuya.png"),
    _item("Kuchen de frutos rojos", "Kuchen de frambuesa o arándanos.", "Tartas", 20000, ["imagenes/kuchen-frambuesa.png", "imagenes/porcion-kuchen.png"]),
    _item("Cheesecake Oreo o Tritón", "Tarta entera.", "Tartas", 25000, ["imagenes/tarta-cheesecake-oreo.png", "imagenes/porcion-cheesecake-oreo.png"]),
    _item("Tarta manjarate", "Tarta entera.", "Tartas", 25000, ["imagenes/tarta-manjarate.png", "imagenes/porcion-manjarate.png"]),
    _item("Porción de torta de bizcocho", UNIDAD, "Porciones", 3500, "imagenes/porciontortadebizcocho.png"),
    _item("Porción de torta amor", UNIDAD, "Porciones", 3500, "imagenes/porcion-torta-amor.png"),
    _item("Porción de pie", f"{UNIDAD} Limón, frambuesa o maracuyá.", "Porciones", 3500, ["imagenes/porcion-pie-limon.png", "imagenes/porcion-pie-frambuesa.png"]),
    _item("Porción de kuchen", f"{UNIDAD} Frambuesa o arándanos.", "Porciones", 3500, "imagenes/porcion-kuchen.png"),
    _item("Porción de cheesecake Oreo o Tritón", UNIDAD, "Porciones", 3500, "imagenes/porcion-cheesecake-oreo.png"),
    _item("Porción de tiramisú", UNIDAD, "Porciones", 3500, "imagenes/porcion-tiramisu.png"),
    _item("Porción de manjarate", UNIDAD, "Porciones", 4000, "imagenes/porcion-manjarate.png"),
    _item("Porción de torta de galleta", UNIDAD, "Porciones", 2500, "imagenes/porcion-torta-galleta.png"),
    _item("Porción de torta de yogurt", UNIDAD, "Porciones", 2500, "imagenes/porcion-torta-yogurt.png"),
    _item(
        "Queques individuales",
        "Caja de 6, uno o dos sabores: vainilla o chocolate con chips, vainilla frambuesa, arándanos, plátano, manzana o limón.",
        "Queques",
        5000,
        "imagenes/queques.png",
    ),
    _item(
        "Cupcakes",
        "Caja de 6, uno o dos sabores: chocolate con salsa de chocolate y crema de menta; vainilla frutilla; vainilla bariloche y chocolate; vainilla manjar plátano.",
        "Cupcakes",
        8000,
        "imagenes/cupcake.png",
    ),
    _item("Opción 1 Día de la madre", "Flor de crochet y cajita con alfajor o mini cuchuflí.", "Día de la madre", 6500, "imagenes/madre-1.jpg"),
    _item("Opción 2 Día de la madre", "Caja de alfajores, 3 mini cuchuflí, 1 galleta glaseada y mini marshmallows.", "Día de la madre", 8000, "imagenes/madre-2.jpg"),
    _item("Opción 3 Día de la madre", "Caja de 6 alfajores (manjar, frambuesa y frutos rojos) y mini marshmallows.", "Día de la madre", 15000, "imagenes/madre-3.jpg"),
    _item("Opción 4 Día de la madre", "Caja surtida con galletas, brownie, alfajores, mini cuchuflí y bombas.", "Día de la madre", 16000, "imagenes/madre-4.jpg"),
    _item("Opción 5 Desayuno Día de la madre", "Desayuno con pie de limón, alfajores, sándwich, frutas, galletas y vela.", "Día de la madre", 27000, "imagenes/madre-5.jpg"),
    _item("Torta Día de la madre", "Bizcocho o galleta, para 10 o 15 personas.", "Día de la madre", 15000, "imagenes/madre-6.jpg", TORTA_FESTIVA),
    _item("Torta Día del padre", "Bizcocho o galleta, para 10 o 15 personas.", "Día del padre", 15000, "imagenes/padre-1.jpg", TORTA_FESTIVA),
    _item("Desayuno Día del padre", "Once salada y dulce: pollo, sándwich, postre, bebida y alfajor.", "Día del padre", 28000, "imagenes/padre-2.jpg"),
    _item("Tabla salada Día del padre", "Quesos, fiambres, aceitunas, snacks y vino o Austral Lager.", "Día del padre", 24000, "imagenes/padre-3.jpg"),
    _item("Frasco Día del padre", "Frasco con 3 galletas chips, 3 Ferrero y 3 Reese's.", "Día del padre", 9000, "imagenes/padre-4.jpg"),
    _item("Caja mixta Día del padre", "Alfajores, aceitunas, pollo crispy, twistos y queso.", "Día del padre", 16000, "imagenes/padre-5.jpg"),
    _item("Caja sándwich Día del padre", "Alfajores, galletas, bebida y sándwich de jamón serrano.", "Día del padre", 17000, "imagenes/padre-6.jpg"),
    _item("Cuchuflís y huevitos", "4 cuchuflí de manjar y 5 huevos Trencito.", "Día de Pascua", 4000, "imagenes/pascua-2.jpg"),
    _item("Huevos rellenos", "Caja de 2 huevos a elección, 9 × 6,5 cm.", "Día de Pascua", 18000, "imagenes/pascua-3.jpg"),
    _item("Cajita de dulces para pintar", "Caja de Pascua con galletas, conejitos, cuchuflí y chocolates.", "Día de Pascua", 16000, "imagenes/pascua-4.jpg"),
    _item("Huevo plano relleno", "Huevo de 10 × 15 cm, Ferrero y Kinder o Oreo con manjar.", "Día de Pascua", 12000, "imagenes/pascua-5.jpg"),
    _item("Alfajores de maicena dieciocheros", "5 unidades.", "Fiestas patrias", 3500, "imagenes/alfajor-maicena.png"),
    _item("Chilenito con coco", "5 unidades, 6 cm.", "Fiestas patrias", 2500, "imagenes/chilenitos.png"),
    _item("Chilenito con merengue", "5 unidades, 6 cm.", "Fiestas patrias", 3000, "imagenes/chilenitoconmerengue.png"),
    _item("Empolvados dieciocheros", "5 unidades.", "Fiestas patrias", 2500, "imagenes/empolvados.png"),
    _item("Kuchen sureño", "Trozo.", "Fiestas patrias", 3500, "imagenes/porcion-kuchen.png"),
    _item("Hojarascas para alfajor", "30 unidades.", "Fiestas patrias", 4500, "imagenes/hojaldrados.png"),
    _item("Berlines mini dieciocheros", "5 unidades.", "Fiestas patrias", 2500, "imagenes/berlines.png"),
    _item("Alfajores de manjar dieciocheros", "5 unidades.", "Fiestas patrias", 6000, "imagenes/alfajor-manjar.png"),
    _item("Galletas de mantequilla dieciocheras", "5 unidades.", "Fiestas patrias", 2500, "imagenes/fiestas-galletas-estrellas.png"),
]
