from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Q
from datetime import datetime, timedelta
from Productos.models import Producto, Proveedor, Categoria, Lote, ProductoConSerial
from movimientos.models import Movimiento
from compras.models import Compra
from usuarios.models import Usuario

@login_required
def dashboard(request):
    """Vista principal del dashboard con estadísticas reales"""

    # ========== ESTADÍSTICAS PRINCIPALES ==========
    total_productos = Producto.objects.count()
    total_proveedores = Proveedor.objects.count()

    # ========== CALCULAR VALOR DEL INVENTARIO Y STOCK TOTAL ==========
    productos = Producto.objects.all()
    valor_inventario = 0
    stock_total = 0  # 🔥 NUEVO
    productos_bajo_stock_list = []  # 🔥 NUEVO

    for p in productos:
        stock = p.stock_total()
        stock_total += stock  # 🔥 NUEVO: Sumar stock total

        if p.precio_venta and stock > 0:
            valor_inventario += float(p.precio_venta) * int(stock)

        if stock <= p.stock_minimo:
            productos_bajo_stock_list.append(p)  # 🔥 NUEVO

    # Compras del mes actual
    hoy = datetime.now()

    compras_mes = Compra.objects.filter(
        fecha__year=hoy.year,
        fecha__month=hoy.month
    ).count()

    # ========== MOVIMIENTOS DE HOY ==========
    movimientos_hoy = Movimiento.objects.filter(
        created_at__date=hoy.date()
    ).count()

    # ========== PRODUCTOS CON BAJO STOCK (CONTEO) ==========
    productos_bajo_stock_count = len(productos_bajo_stock_list)  # 🔥 ACTUALIZADO
    productos_criticos = productos_bajo_stock_list[:5]  # 🔥 ACTUALIZADO

    # Usuarios activos
    usuarios_activos = Usuario.objects.filter(is_active=True).count()

    # ========== TABLAS RECIENTES ==========
    ultimas_compras = Compra.objects.all().order_by('-fecha')[:5]

    ultimos_movimientos = Movimiento.objects.all().order_by(
        '-created_at'
    )[:10]

    ultimos_usuarios = Usuario.objects.all().order_by(
        '-date_joined'
    )[:5]

    ultimos_proveedores = Proveedor.objects.all().order_by(
        '-created_at'
    )[:5]

    # ========== ESTADÍSTICAS DE LOTES Y SERIALES ==========
    lotes_pendientes = Lote.objects.filter(estado='pendiente').count()
    lotes_parciales = Lote.objects.filter(estado='parcial').count()
    lotes_completados = Lote.objects.filter(estado='completado').count()
    lotes_agotados = Lote.objects.filter(estado='agotado').count()

    total_lotes = (
        lotes_pendientes +
        lotes_parciales +
        lotes_completados +
        lotes_agotados
    )

    seriales_disponibles = ProductoConSerial.objects.filter(
        estado='disponible'
    ).count()

    seriales_vendidos = ProductoConSerial.objects.filter(
        estado='vendido'
    ).count()

    total_seriales = ProductoConSerial.objects.count()

    ultimos_lotes = Lote.objects.all().order_by('-created_at')[:5]

    # ========== DATOS PARA GRÁFICOS ==========
    fechas = []
    movimientos_por_dia = []

    for i in range(6, -1, -1):
        fecha = hoy.date() - timedelta(days=i)

        fechas.append(fecha.strftime('%d/%m'))

        count = Movimiento.objects.filter(
            created_at__date=fecha
        ).count()

        movimientos_por_dia.append(count)

    # Productos por categoría
    categorias_nombres = []
    categorias_cantidades = []

    for categoria in Categoria.objects.all():
        categorias_nombres.append(categoria.nombre)
        categorias_cantidades.append(
            categoria.producto_set.count()
        )

    if not categorias_nombres:
        categorias_nombres = ['Sin categorías']
        categorias_cantidades = [0]

    context = {
        # Estadísticas
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock_count,
        'compras_mes': compras_mes,
        'usuarios_activos': usuarios_activos,
        'movimientos_hoy': movimientos_hoy,
        'valor_inventario': int(valor_inventario),
        'total_proveedores': total_proveedores,
        'stock_total': stock_total,  # 🔥 NUEVO
        'total_bajo_stock': len(productos_bajo_stock_list),  # 🔥 NUEVO

        # Tablas
        'ultimos_movimientos': ultimos_movimientos,
        'ultimas_compras': ultimas_compras,
        'ultimos_usuarios': ultimos_usuarios,
        'ultimos_proveedores': ultimos_proveedores,
        'productos_criticos': productos_criticos,

        # Lotes y seriales
        'lotes_pendientes': lotes_pendientes,
        'lotes_parciales': lotes_parciales,
        'lotes_completados': lotes_completados,
        'lotes_agotados': lotes_agotados,
        'total_lotes': total_lotes,
        'seriales_disponibles': seriales_disponibles,
        'seriales_vendidos': seriales_vendidos,
        'total_seriales': total_seriales,
        'ultimos_lotes': ultimos_lotes,

        # Gráficos
        'fechas_grafico': fechas,
        'movimientos_grafico': movimientos_por_dia,
        'categorias_nombres': categorias_nombres,
        'categorias_cantidades': categorias_cantidades,
    }

    return render(request, 'dashboard.html', context)