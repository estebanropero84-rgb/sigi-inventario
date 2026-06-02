from django.db import models
from usuarios.models import Usuario

# ========== CATEGORÍA ==========
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre


# ========== BODEGA ==========
class Bodega(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    encargado = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre


# ========== PRODUCTO ==========
class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    bodega = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    garantia_meses = models.IntegerField(default=12, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def valor_inventario(self):
        return self.stock_actual * self.precio_venta if self.precio_venta else 0


# ========== PROVEEDOR ==========
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre


# ========== LOTE ==========
class Lote(models.Model):
    ESTADOS = (
        ('pendiente', '⏳ Pendiente'),
        ('parcial', '📦 Recibido Parcial'),
        ('completado', '✅ Completado'),
        ('cancelado', '❌ Cancelado'),
    )
    
    codigo = models.CharField(max_length=50, unique=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='lotes')
    
    cantidad_total = models.IntegerField(default=0)
    cantidad_recibida = models.IntegerField(default=0)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    fecha_pedido = models.DateField(auto_now_add=True)
    fecha_estimada = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.producto.nombre}"
    
    @property
    def restante(self):
        return self.cantidad_total - self.cantidad_recibida
    
    @property
    def porcentaje_recibido(self):
        if self.cantidad_total > 0:
            return int((self.cantidad_recibida / self.cantidad_total) * 100)
        return 0


# ========== PRODUCTO CON SERIAL ==========
class ProductoConSerial(models.Model):
    ESTADOS_SERIAL = (
        ('disponible', '✅ Disponible'),
        ('vendido', '💰 Vendido'),
        ('danado', '⚠️ Dañado'),
        ('devuelto', '🔄 Devuelto'),
        ('reservado', '📌 Reservado'),
    )
    
    serial = models.CharField(max_length=100, unique=True)
    producto_base = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='unidades')
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='productos')
    
    estado = models.CharField(max_length=20, choices=ESTADOS_SERIAL, default='disponible')
    notas = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.serial} - {self.producto_base.nombre}"
    
    class Meta:
        ordering = ['serial']


# ========== REGISTRO DE RECEPCIÓN DE LOTES ==========
class RecepcionLote(models.Model):
    lote = models.ForeignKey(Lote, on_delete=models.CASCADE, related_name='recepciones')
    cantidad = models.IntegerField()
    seriales = models.TextField(help_text="Lista de seriales recibidos (uno por línea)")
    recibido_por = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    notas = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recepción {self.id} - {self.lote.codigo} - {self.cantidad} unidades"


# ========== BITÁCORA ==========
class LogActividad(models.Model):
    ACCIONES = (
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('ver', 'Ver'),
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('exportar', 'Exportar'),
        ('importar', 'Importar'),
    )
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modelo = models.CharField(max_length=50)
    objeto_id = models.IntegerField(null=True, blank=True)
    objeto_nombre = models.CharField(max_length=200, blank=True, null=True)
    detalles = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.usuario} - {self.accion} - {self.modelo} - {self.fecha}"