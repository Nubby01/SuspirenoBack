# Variantes y extras del catálogo.

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pasteleria', '0002_cotizacion_creada_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizacionproducto',
            name='formato',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.AddField(
            model_name='pedidoproducto',
            name='formato',
            field=models.CharField(blank=True, default='', max_length=80),
        ),
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.CharField(choices=[('Rollitos tradicionales', 'Rollitos tradicionales'), ('Rollitos de canela sabores', 'Rollitos de canela sabores'), ('Alfajores 100% artesanales', 'Alfajores 100% artesanales'), ('Alfajores tradicionales', 'Alfajores tradicionales'), ('Alfajores artesanales', 'Alfajores artesanales'), ('Bombitas', 'Bombitas'), ('Productos mini', 'Productos mini'), ('Berlines', 'Berlines'), ('Untables', 'Untables'), ('Tortas y pies', 'Tortas y pies'), ('Tortas', 'Tortas'), ('Tartas', 'Tartas'), ('Porciones', 'Porciones'), ('Cupcakes', 'Cupcakes'), ('Galletas', 'Galletas'), ('San Valentín', 'San Valentín')], default='Tortas', max_length=40),
        ),
        migrations.CreateModel(
            name='Variante',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('formato', models.CharField(max_length=80)),
                ('precio', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variantes', to='pasteleria.producto')),
            ],
            options={
                'ordering': ['orden', 'id'],
                'constraints': [models.UniqueConstraint(fields=('producto', 'formato'), name='variante_formato_unico'), models.CheckConstraint(condition=models.Q(('precio__gt', 0)), name='variante_precio_positivo')],
            },
        ),
    ]
