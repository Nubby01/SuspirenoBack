# Opción de producto agotado.
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pasteleria", "0006_categorias_dulces_sabores"),
    ]

    operations = [
        migrations.AddField(
            model_name="producto",
            name="opciones",
            field=models.CharField(
                blank=True,
                help_text="Ejemplo: Relleno:café,menta,limón,chocolate,frambuesa",
                max_length=300,
            ),
        ),
        migrations.AddField(
            model_name="producto",
            name="agotado",
            field=models.BooleanField(default=False, help_text="Marca Sin stock en el catálogo."),
        ),
    ]
