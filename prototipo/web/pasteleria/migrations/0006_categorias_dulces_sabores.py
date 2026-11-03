# Categorías de dulces y sabores.
from django.db import migrations, models


ANTIGUAS = {
    "Rollitos tradicionales": "Rollitos dulces",
    "Rollitos de canela sabores": "Rollitos dulces",
    "Alfajores artesanales": "Alfajores sabores",
}


def reasignar(apps, schema_editor):
    Producto = apps.get_model("pasteleria", "Producto")
    for vieja, nueva in ANTIGUAS.items():
        Producto.objects.filter(categoria=vieja).update(categoria=nueva)
    Producto.objects.filter(nombre__in=["Rollos de pizza (tomate, queso y orégano)", "Rollo de ajo"]).update(
        categoria="Rollitos salados"
    )
    Producto.objects.filter(
        nombre__in=["Alfajor manjar mate", "Alfajor mantecatto", "Alfajor tiramisú"]
    ).update(disponible=False)


class Migration(migrations.Migration):
    dependencies = [
        ("pasteleria", "0005_grupos_festividades"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producto",
            name="categoria",
            field=models.CharField(
                choices=[
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
                ],
                default="Tortas",
                max_length=40,
            ),
        ),
        migrations.RunPython(reasignar, migrations.RunPython.noop),
    ]
