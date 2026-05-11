from django.db import models
from Productos.models import Producto
from usuarios.models import Usuario

class Movimiento(models.Model):
    TIPOS = (
        ('entrada', '📥 Entrada'),
        ('salida', '📤 Salida'),
    )
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    cantidad = models.IntegerField()
    stock_anterior = models.IntegerField(default=0)
    stock_nuevo = models.IntegerField(default=0)
    motivo = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} - {self.cantidad}"