from django.db import models

# Categoría de productos
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

# Producto
class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50, blank=True)
    modelo = models.CharField(max_length=50, blank=True)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    ubicacion = models.CharField(max_length=100, blank=True)
    garantia_meses = models.IntegerField(default=12)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def valor_inventario(self):
        return self.stock_actual * self.precio_venta if self.precio_venta else 0