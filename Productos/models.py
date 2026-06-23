from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from usuarios.models import Usuario
from decimal import Decimal

# ========== UBICACIÓN ==========
class Ubicacion(models.Model):
    """Ubicaciones predefinidas para productos"""
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'


# ========== CATEGORÍA ==========
class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'


# ========== BODEGA ==========
class Bodega(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    encargado = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'


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
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'


# ========== PRODUCTO ==========
class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    codigo_barras = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="Opcional - Déjalo vacío si no tiene código de barras"
    )
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    bodega = models.ForeignKey(Bodega, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    
    stock_minimo = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0, 'El stock mínimo no puede ser negativo')]
    )
    precio_compra = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0'), 'El precio de compra no puede ser negativo')]
    )
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'), 'El precio de venta no puede ser negativo')]
    )
    
    ubicacion = models.ForeignKey(
        Ubicacion, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='productos',
        help_text="Selecciona una ubicación predefinida"
    )
    
    garantia_meses = models.IntegerField(default=12, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def stock_total(self):
        total = 0
        for lote in self.lotes.filter(estado__in=['completado', 'parcial']):
            total += lote.cantidad_recibida - lote.cantidad_vendida
        return total
    
    def stock_actual(self):
        return self.stock_total()
    
    @property
    def valor_inventario(self):
        return self.stock_total() * (self.precio_venta or 0)
    
    def get_ubicacion_nombre(self):
        return self.ubicacion.nombre if self.ubicacion else 'Sin ubicación'
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'


# ========== LOTE ==========
class Lote(models.Model):
    ESTADOS = (
        ('pendiente', '⏳ Pendiente'),
        ('parcial', '📦 Recibido Parcial'),
        ('completado', '✅ Completado'),
        ('agotado', '🚫 Agotado'),
        ('cancelado', '❌ Cancelado'),
    )
    
    codigo = models.CharField(max_length=50, unique=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='lotes')
    
    cantidad_total = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, 'La cantidad total no puede ser negativa')]
    )
    cantidad_recibida = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, 'La cantidad recibida no puede ser negativa')]
    )
    cantidad_vendida = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, 'La cantidad vendida no puede ser negativa')]
    )
    
    costo_unitario = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0'), 'El costo unitario no puede ser negativo')]
    )
    
    fecha_pedido = models.DateField(auto_now_add=True)
    fecha_estimada = models.DateField(null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True, help_text="Fecha de ingreso del lote - Usado para FIFO")
    
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
    def disponible(self):
        return self.cantidad_recibida - self.cantidad_vendida
    
    @property
    def porcentaje_recibido(self):
        if self.cantidad_total > 0:
            return int((self.cantidad_recibida / self.cantidad_total) * 100)
        return 0
    
    def puede_vender(self, cantidad):
        return self.disponible >= cantidad
    
    def vender(self, cantidad):
        if not self.puede_vender(cantidad):
            raise ValueError(f"No hay suficiente stock en el lote {self.codigo}. Disponible: {self.disponible}")
        self.cantidad_vendida += cantidad
        self.save()
        self.actualizar_estado()
        return True
    
    def actualizar_estado(self):
        if self.disponible <= 0:
            self.estado = 'agotado'
        elif self.cantidad_recibida < self.cantidad_total:
            self.estado = 'parcial'
        elif self.cantidad_recibida >= self.cantidad_total and self.disponible > 0:
            self.estado = 'completado'
        self.save()
    
    class Meta:
        ordering = ['fecha_ingreso']


# ========== MOVIMIENTO (CORREGIDO) ==========
class Movimiento(models.Model):
    """Historial de todos los movimientos del producto"""
    TIPO_CHOICES = [
        ('entrada', '📥 Entrada (Compra)'),
        ('salida', '📤 Salida (Venta)'),
        ('ajuste', '🔧 Ajuste de Inventario'),
        ('devolucion', '🔄 Devolución'),
        ('traslado', '🚚 Traslado entre bodegas'),
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    lote = models.ForeignKey(Lote, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1, 'La cantidad debe ser mayor a 0')]
    )
    descripcion = models.TextField(blank=True, null=True)
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='productos_movimientos'  # 🔥 CORREGIDO: related_name único
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})"
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'


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
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1, 'La cantidad debe ser mayor a 0')]
    )
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
    
    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividad'