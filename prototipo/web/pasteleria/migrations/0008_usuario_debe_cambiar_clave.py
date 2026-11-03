# Flag de clave provisoria.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pasteleria", "0007_opciones_agotado"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="debe_cambiar_clave",
            field=models.BooleanField(
                default=False,
                help_text="Si es verdadero, debe cambiar la clave al ingresar.",
            ),
        ),
    ]
