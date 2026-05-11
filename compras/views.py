from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Compra, CompraDetalle
from Productos.models import Producto, Proveedor
from .forms import CompraForm

@login_required
def listar_compras(request):
    compras = Compra.objects.all().order_by('-fecha')
    return render(request, 'compras/lista.html', {'compras': compras})

@login_required
def crear_compra(request):
    """Crear nueva orden de compra con autocompletado de proveedores"""
    
    productos = Producto.objects.all().order_by('nombre')
    proveedores = Proveedor.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        proveedor = request.POST.get('proveedor')
        fecha = request.POST.get('fecha')
        observaciones = request.POST.get('observaciones', '')
        
        if not proveedor:
            messages.error(request, 'El proveedor es obligatorio')
            return render(request, 'compras/crear.html', {
                'productos': productos,
                'proveedores': proveedores,
                'form': CompraForm()
            })
        
        compra = Compra.objects.create(
            proveedor=proveedor,
            fecha=fecha,
            observaciones=observaciones,
            usuario=request.user,
            estado='pendiente',
            total=0
        )
        
        total_compra = 0
        
        for key, value in request.POST.items():
            if key.startswith('producto_'):
                idx = key.split('_')[1]
                producto_id = value
                cantidad = request.POST.get(f'cantidad_{idx}', 0)
                precio = request.POST.get(f'precio_{idx}', 0)
                
                if producto_id and int(cantidad) > 0:
                    producto = Producto.objects.get(id=producto_id)
                    subtotal = int(cantidad) * float(precio)
                    total_compra += subtotal
                    
                    CompraDetalle.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio,
                        subtotal=subtotal
                    )
        
        compra.total = total_compra
        compra.save()
        
        messages.success(request, f'Compra #{compra.id} creada exitosamente')
        return redirect('compras:listar')
    
    return render(request, 'compras/crear.html', {
        'productos': productos,
        'proveedores': proveedores,
        'form': CompraForm()
    })


@login_required
def ver_compra(request, pk):
    """Ver detalle de una compra"""
    compra = get_object_or_404(Compra, pk=pk)
    detalles = compra.detalles.all()
    
    return render(request, 'compras/ver.html', {
        'compra': compra,
        'detalles': detalles
    })


@login_required
def recibir_compra(request, pk):
    """Recibir una compra y actualizar el inventario"""
    compra = get_object_or_404(Compra, pk=pk)
    
    if request.method == 'POST':
        for detalle in compra.detalles.all():
            producto = detalle.producto
            producto.stock_actual += detalle.cantidad
            producto.save()
        
        compra.estado = 'recibido'
        compra.save()
        
        messages.success(request, f'✅ Compra #{compra.id} recibida. El inventario ha sido actualizado.')
        return redirect('compras:listar')
    
    return render(request, 'compras/recibir.html', {'compra': compra})


# ========== API PARA OBTENER ÚLTIMO PRECIO ==========

@login_required
def api_ultimo_precio(request, producto_id):
    """Retorna el último precio de compra de un producto"""
    try:
        # Buscar el último detalle de compra para este producto
        ultimo_detalle = CompraDetalle.objects.filter(
            producto_id=producto_id
        ).order_by('-compra__fecha').first()
        
        if ultimo_detalle:
            precio = float(ultimo_detalle.precio_unitario)
        else:
            # Si no hay compras previas, usar el precio de venta del producto
            producto = Producto.objects.get(id=producto_id)
            precio = float(producto.precio_venta) if producto.precio_venta else 0
        
        return JsonResponse({'precio': precio, 'success': True})
    except Exception as e:
        return JsonResponse({'precio': None, 'error': str(e), 'success': False})