from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Movimiento
from Productos.models import Producto
from .forms import MovimientoForm

@login_required
def listar_movimientos(request):
    movimientos = Movimiento.objects.all().order_by('-created_at')
    return render(request, 'movimientos/lista.html', {'movimientos': movimientos})

@login_required
def registrar_movimiento(request):
    """Registrar entrada o salida de inventario"""
    
    # 🔥 Obtener todos los productos
    productos = Producto.objects.all().order_by('nombre')
    
    # Debug: imprimir en consola
    print(f"Productos encontrados: {productos.count()}")
    for p in productos:
        print(f"  - {p.nombre} (ID: {p.id}) - Stock: {p.stock_actual}")
    
    if request.method == 'POST':
        producto_id = request.POST.get('producto')
        tipo = request.POST.get('tipo')
        cantidad = request.POST.get('cantidad')
        motivo = request.POST.get('motivo', '')
        observacion = request.POST.get('observacion', '')
        
        if not producto_id or not tipo or not cantidad:
            messages.error(request, 'Complete todos los campos obligatorios')
            return redirect('movimientos:registrar')
        
        producto = get_object_or_404(Producto, pk=producto_id)
        cantidad = int(cantidad)
        stock_anterior = producto.stock_actual
        
        # Calcular nuevo stock
        if tipo == 'entrada':
            stock_nuevo = stock_anterior + cantidad
        else:  # salida
            if cantidad > stock_anterior:
                messages.error(request, f'No hay suficiente stock. Stock actual: {stock_anterior}')
                return render(request, 'movimientos/registrar.html', {
                    'productos': productos,
                    'form': MovimientoForm()
                })
            stock_nuevo = stock_anterior - cantidad
        
        # Crear movimiento
        movimiento = Movimiento.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cantidad,
            stock_anterior=stock_anterior,
            stock_nuevo=stock_nuevo,
            motivo=motivo,
            observacion=observacion,
            usuario=request.user
        )
        
        # Actualizar stock del producto
        producto.stock_actual = stock_nuevo
        producto.save()
        
        messages.success(request, f'✅ Movimiento registrado: {tipo} de {cantidad} unidades de {producto.nombre}')
        return redirect('movimientos:listar')
    
    return render(request, 'movimientos/registrar.html', {
        'productos': productos,
        'form': MovimientoForm()
    })