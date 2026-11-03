# Varias fotos por producto.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pasteleria", "0003_catalogo_variantes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producto",
            name="imagen_url",
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name="producto",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("Rollitos tradicionales", "Rollitos tradicionales"),
                    ("Rollitos de canela sabores", "Rollitos de canela sabores"),
                    ("Alfajores 100% artesanales", "Alfajores 100% artesanales"),
                    ("Alfajores tradicionales", "Alfajores tradicionales"),
                    ("Alfajores artesanales", "Alfajores artesanales"),
                    ("Bombitas", "Bombitas"),
                    ("Productos mini", "Productos mini"),
                    ("Berlines", "Berlines"),
                    ("Untables", "Untables"),
                    ("Tortas y pies", "Tortas y pies"),
                    ("Tortas", "Tortas"),
                    ("Tartas", "Tartas"),
                    ("Porciones", "Porciones"),
                    ("Queques", "Queques"),
                    ("Cupcakes", "Cupcakes"),
                    ("Galletas", "Galletas"),
                    ("San Valentín", "San Valentín"),
                ],
                default="Tortas",
                max_length=40,
            ),
        ),
    ]
