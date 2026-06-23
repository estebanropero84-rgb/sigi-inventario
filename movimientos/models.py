from django.db import models
from django.conf import settings
from Productos.models import Producto, Lote


class Movimiento(models.Model):
    TIPO_CHOICES = [
        ('entrada', '📥 Entrada'),
        ('salida', '📤 Salida'),
        ('devolucion', '🔄 Devolución'),
        ('ajuste', '🔧 Ajuste'),
        ('traslado', '🚚 Traslado'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(default=1)
    serial = models.CharField(max_length=100, blank=True, null=True)
    stock_anterior = models.IntegerField(default=0)
    stock_nuevo = models.IntegerField(default=0)
    motivo = models.CharField(max_length=100, blank=True, null=True)
    observacion = models.TextField(blank=True, null=True)
    
    # 🔥 CORREGIDO: Usar settings.AUTH_USER_MODEL
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'