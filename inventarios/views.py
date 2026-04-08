from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Count
from datetime import datetime
from Productos.models import Producto
from movimientos.models import Movimiento
from compras.models import Compra
from usuarios.models import Usuario

@login_required
def dashboard(request):
    """
    Vista principal del dashboard con estadísticas reales
    """
    # Obtener todos los productos
    productos = Producto.objects.all()
    
    # Calcular valor total del inventario
    valor_inventario = 0
    for p in productos:
        if p.precio_venta and p.stock_actual:
            valor_inventario += float(p.precio_venta) * int(p.stock_actual)
    
    # Obtener compras del mes actual
    compras_mes = Compra.objects.filter(
        fecha__year=datetime.now().year,
        fecha__month=datetime.now().month
    ).count()
    
    # Obtener movimientos de hoy
    movimientos_hoy = Movimiento.objects.filter(
        created_at__date=datetime.now().date()
    ).count()
    
    # Productos con bajo stock
    productos_bajo_stock = productos.filter(stock_actual__lte=F('stock_minimo')).count()
    
    # Usuarios activos
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    
    # 🔥 Obtener últimos 5 usuarios para mostrar en el dashboard
    ultimos_usuarios = Usuario.objects.all().order_by('-date_joined')[:5]
    
    # Últimos movimientos
    ultimos_movimientos = Movimiento.objects.all().order_by('-created_at')[:10]
    
    # Productos críticos (stock bajo)
    productos_criticos = productos.filter(stock_actual__lte=F('stock_minimo'))[:5]
    
    context = {
        'total_productos': productos.count(),
        'productos_bajo_stock': productos_bajo_stock,
        'compras_mes': compras_mes,
        'usuarios_activos': usuarios_activos,
        'movimientos_hoy': movimientos_hoy,
        'valor_inventario': int(valor_inventario),
        'ultimos_movimientos': ultimos_movimientos,
        'productos_criticos': productos_criticos,
        'ultimos_usuarios': ultimos_usuarios,  #  Agregar usuarios al contexto
    }
    
    return render(request, 'dashboard.html', context)
