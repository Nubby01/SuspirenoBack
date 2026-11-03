# Grupos de festividades en el menú.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pasteleria", "0004_fotos_carrusel"),
    ]

    operations = [
        migrations.AlterField(
            model_name="producto",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("Rollitos tradicionales", "Canela"),
                    ("Rollitos de canela sabores", "Sabores"),
                    ("Alfajores artesanales", "Artesanales"),
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
    ]
