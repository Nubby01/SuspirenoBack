# Migración inicial de modelos.

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80)),
                ('telefono', models.CharField(max_length=20, unique=True)),
                ('direccion', models.CharField(blank=True, max_length=160)),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('rol', models.CharField(choices=[('administradora', 'Administradora'), ('ayudante', 'Ayudante'), ('pendiente', 'Pendiente de habilitación')], default='pendiente', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'usuario',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cotizacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=datetime.date.today)),
                ('estado', models.CharField(choices=[('Enviada', 'Enviada'), ('Convertida', 'Convertida')], default='Enviada', max_length=20)),
                ('total', models.PositiveIntegerField(default=0)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cotizaciones', to='pasteleria.cliente')),
            ],
            options={
                'ordering': ['-fecha', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Insumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, unique=True)),
                ('stock_actual', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('stock_minimo', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('unidad_medida', models.CharField(choices=[('kg', 'kg'), ('g', 'g'), ('L', 'L'), ('un', 'un')], max_length=10)),
            ],
            options={
                'ordering': ['nombre'],
                'constraints': [models.CheckConstraint(condition=models.Q(('stock_actual__gte', 0)), name='insumo_stock_no_negativo')],
            },
        ),
        migrations.CreateModel(
            name='CompraInsumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80)),
                ('fecha_vencimiento', models.DateField(blank=True, null=True)),
                ('proveedor', models.CharField(max_length=80)),
                ('precio_compra', models.PositiveIntegerField()),
                ('cantidad_comprada', models.FloatField(validators=[django.core.validators.MinValueValidator(0.001)])),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='compras', to='pasteleria.insumo')),
            ],
            options={
                'ordering': ['fecha_vencimiento', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_pedido', models.DateField(default=datetime.date.today)),
                ('fecha_entrega', models.DateField()),
                ('monto_total', models.PositiveIntegerField()),
                ('abono', models.PositiveIntegerField(default=0)),
                ('estado', models.CharField(choices=[('Pendiente', 'Pendiente'), ('Confirmado', 'Confirmado'), ('En preparación', 'En preparación'), ('Listo', 'Listo'), ('Entregado', 'Entregado'), ('Cancelado', 'Cancelado')], default='Pendiente', max_length=20)),
                ('canal_despacho', models.CharField(choices=[('Retiro', 'Retiro'), ('Despacho', 'Despacho')], max_length=10)),
                ('stock_descontado', models.BooleanField(default=False)),
                ('cotizacion', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='pedido', to='pasteleria.cotizacion')),
                ('registrado_por', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pedidos', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-fecha_pedido', '-id'],
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80)),
                ('descripcion', models.CharField(blank=True, max_length=240)),
                ('categoria', models.CharField(choices=[('Tortas', 'Tortas'), ('Cupcakes', 'Cupcakes'), ('Galletas', 'Galletas')], default='Tortas', max_length=40)),
                ('precio', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('imagen', models.ImageField(blank=True, upload_to='productos/')),
                ('imagen_url', models.CharField(blank=True, max_length=200)),
                ('disponible', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['nombre'],
                'indexes': [models.Index(fields=['categoria', 'disponible'], name='pasteleria__categor_29da7b_idx')],
                'constraints': [models.CheckConstraint(condition=models.Q(('precio__gt', 0)), name='producto_precio_positivo')],
            },
        ),
        migrations.CreateModel(
            name='PedidoProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField()),
                ('precio', models.PositiveIntegerField()),
                ('subtotal', models.PositiveIntegerField()),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lineas', to='pasteleria.pedido')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lineas_pedido', to='pasteleria.producto')),
            ],
        ),
        migrations.CreateModel(
            name='CotizacionProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('precio', models.PositiveIntegerField()),
                ('subtotal', models.PositiveIntegerField()),
                ('cotizacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lineas', to='pasteleria.cotizacion')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lineas_cotizacion', to='pasteleria.producto')),
            ],
        ),
        migrations.CreateModel(
            name='ProductoInsumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.FloatField(validators=[django.core.validators.MinValueValidator(0.001)])),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='usado_en', to='pasteleria.insumo')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receta', to='pasteleria.producto')),
            ],
        ),
        migrations.AddIndex(
            model_name='usuario',
            index=models.Index(fields=['rol'], name='pasteleria__rol_57bd83_idx'),
        ),
        migrations.AddIndex(
            model_name='cotizacion',
            index=models.Index(fields=['estado'], name='pasteleria__estado_135ad4_idx'),
        ),
        migrations.AddIndex(
            model_name='pedido',
            index=models.Index(fields=['estado'], name='pasteleria__estado_8e1bbe_idx'),
        ),
        migrations.AddIndex(
            model_name='pedido',
            index=models.Index(fields=['fecha_entrega'], name='pasteleria__fecha_e_09adcc_idx'),
        ),
        migrations.AddConstraint(
            model_name='pedido',
            constraint=models.CheckConstraint(condition=models.Q(('abono__lte', models.F('monto_total'))), name='pedido_abono_no_supera_total'),
        ),
        migrations.AddConstraint(
            model_name='productoinsumo',
            constraint=models.UniqueConstraint(fields=('producto', 'insumo'), name='receta_sin_insumo_repetido'),
        ),
    ]
