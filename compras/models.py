from django.db import models
from django.conf import settings
from Productos.models import Proveedor


class Compra(models.Model):
    ESTADOS = [
        ('pendiente', '⏳ Pendiente'),
        ('recibido', '✅ Recibido'),
        ('cancelado', '❌ Cancelado'),
    ]
    
    # 🔥 CORREGIDO: ForeignKey a Proveedor
    proveedor = models.ForeignKey(
        Proveedor, 
        on_delete=models.CASCADE,
        db_column='proveedor_id'  # 🔥 Nombre correcto de la columna
    )
    fecha = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre}"
    
    class Meta:
        ordering = ['-fecha']


class CompraDetalle(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('Productos.Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"