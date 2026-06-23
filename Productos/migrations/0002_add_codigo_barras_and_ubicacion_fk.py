# Productos/migrations/0002_add_codigo_barras_and_ubicacion_fk.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Productos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='codigo_barras',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                unique=True,
                help_text="Opcional - Déjalo vacío si no tiene código de barras"
            ),
        ),
        migrations.AddField(
            model_name='producto',
            name='ubicacion',
            field=models.ForeignKey(
                to='Productos.ubicacion',
                on_delete=django.db.models.deletion.SET_NULL,
                null=True,
                blank=True,
                related_name='productos',
                help_text="Selecciona una ubicación predefinida"
            ),
        ),
    ]