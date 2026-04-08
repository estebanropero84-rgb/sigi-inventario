from django.db import models
from Productos.models import Producto
from usuarios.models import Usuario

class Compra(models.Model):
    ESTADOS = (
        ('pendiente', '⏳ Pendiente'),
        ('recibido', '✅ Recibido'),
        ('cancelado', '❌ Cancelado'),
    )
    
    proveedor = models.CharField(max_length=100)
    fecha = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"OC-{self.id} - {self.proveedor}"

class CompraDetalle(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.compra.id} - {self.producto.nombre}"