from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Compra, CompraDetalle
from Productos.models import Producto
from .forms import CompraForm

@login_required
def listar_compras(request):
    compras = Compra.objects.all().order_by('-fecha')
    return render(request, 'compras/lista.html', {'compras': compras})

@login_required
def crear_compra(request):
    """Crear nueva orden de compra"""
    
    productos = Producto.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        proveedor = request.POST.get('proveedor')
        fecha = request.POST.get('fecha')
        observaciones = request.POST.get('observaciones', '')
        
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
        'form': CompraForm()
    })


# ========== NUEVAS FUNCIONES ==========

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
        # Actualizar stock de cada producto
        for detalle in compra.detalles.all():
            producto = detalle.producto
            producto.stock_actual += detalle.cantidad
            producto.save()
        
        # Cambiar estado de la compra
        compra.estado = 'recibido'
        compra.save()
        
        messages.success(request, f'✅ Compra #{compra.id} recibida. El inventario ha sido actualizado.')
        return redirect('compras:listar')
    
    return render(request, 'compras/recibir.html', {'compra': compra})