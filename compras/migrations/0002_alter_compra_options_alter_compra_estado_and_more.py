import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def migrar_proveedores_a_fk(apps, schema_editor):
    Compra = apps.get_model('compras', 'Compra')
    Proveedor = apps.get_model('Productos', 'Proveedor')

    for compra in Compra.objects.all():
        nombre_texto = (compra.proveedor_nombre_temp or '').strip()
        if not nombre_texto:
            compra.proveedor_fk = None
            compra.save()
            continue

        proveedor = Proveedor.objects.filter(nombre__iexact=nombre_texto).first()
        if not proveedor:
            proveedor = Proveedor.objects.create(nombre=nombre_texto)

        compra.proveedor_fk = proveedor
        compra.save()


def revertir_proveedores(apps, schema_editor):
    Compra = apps.get_model('compras', 'Compra')
    for compra in Compra.objects.all():
        if compra.proveedor_fk_id:
            compra.proveedor_nombre_temp = compra.proveedor_fk.nombre
            compra.save()


class Migration(migrations.Migration):

    dependencies = [
        ('Productos', '0001_initial'),
        ('compras', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compra',
            options={'ordering': ['-fecha']},
        ),

        # 1. Renombramos el campo viejo de texto, solo para no perder el dato
        migrations.RenameField(
            model_name='compra',
            old_name='proveedor',
            new_name='proveedor_nombre_temp',
        ),

        # 2. Agregamos el nuevo campo FK, temporalmente nullable
        migrations.AddField(
            model_name='compra',
            name='proveedor_fk',
            field=models.ForeignKey(
                to='Productos.proveedor',
                on_delete=django.db.models.deletion.CASCADE,
                null=True,
                blank=True,
            ),
        ),

        # 3. Migramos los datos: texto -> Proveedor real
        migrations.RunPython(migrar_proveedores_a_fk, revertir_proveedores),

        # 4. Eliminamos el campo viejo de texto
        migrations.RemoveField(
            model_name='compra',
            name='proveedor_nombre_temp',
        ),

        # 5. Renombramos el campo FK a su nombre final 'proveedor'
        migrations.RenameField(
            model_name='compra',
            old_name='proveedor_fk',
            new_name='proveedor',
        ),

        # 6. Lo dejamos obligatorio (sin null) y con el db_column correcto
        migrations.AlterField(
            model_name='compra',
            name='proveedor',
            field=models.ForeignKey(
                to='Productos.proveedor',
                on_delete=django.db.models.deletion.CASCADE,
                db_column='proveedor_id',
            ),
        ),

        # --- resto de tus cambios originales, sin modificar ---
        migrations.AlterField(
            model_name='compra',
            name='estado',
            field=models.CharField(choices=[('pendiente', '⏳ Pendiente'), ('recibido', '✅ Recibido'), ('cancelado', '❌ Cancelado')], default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='compra',
            name='observaciones',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='compra',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='compra',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='compradetalle',
            name='precio_unitario',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
        migrations.AlterField(
            model_name='compradetalle',
            name='subtotal',
            field=models.DecimalField(decimal_places=2, max_digits=12),
        ),
    ]