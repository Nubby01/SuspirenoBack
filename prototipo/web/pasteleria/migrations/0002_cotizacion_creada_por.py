# Cotización queda ligada a quien la armó.

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pasteleria', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizacion',
            name='creada_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cotizaciones', to=settings.AUTH_USER_MODEL),
        ),
    ]
