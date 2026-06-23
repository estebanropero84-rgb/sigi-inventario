from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from .models import Compra, CompraDetalle
from Productos.models import Producto, Proveedor, Lote
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
        print("🔍 POST recibido:", request.POST)
        proveedor_id = request.POST.get('proveedor')
        fecha = request.POST.get('fecha')
        observaciones = request.POST.get('observaciones', '')
        
        if not proveedor_id:
            messages.error(request, '❌ El proveedor es obligatorio')
            return render(request, 'compras/crear.html', {
                'productos': productos,
                'proveedores': proveedores,
                'form': CompraForm()
            })
        
        try:
            proveedor_id = int(proveedor_id)
        except (ValueError, TypeError):
            messages.error(request, f'❌ El proveedor seleccionado no es válido.')
            return render(request, 'compras/crear.html', {
                'productos': productos,
                'proveedores': proveedores,
                'form': CompraForm()
            })
        
        if not fecha:
            messages.error(request, '❌ La fecha es obligatoria')
            return render(request, 'compras/crear.html', {
                'productos': productos,
                'proveedores': proveedores,
                'form': CompraForm()
            })
        
        try:
            proveedor = Proveedor.objects.get(id=proveedor_id)
        except Proveedor.DoesNotExist:
            messages.error(request, f'❌ El proveedor no existe.')
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
        detalles_creados = 0
        
        for key, value in request.POST.items():
            if key.startswith('producto_'):
                idx = key.split('_')[1]
                producto_id = value
                cantidad_str = request.POST.get(f'cantidad_{idx}', '')
                precio_str = request.POST.get(f'precio_{idx}', '')
                
                if not producto_id:
                    continue
                
                try:
                    producto_id = int(producto_id)
                except (ValueError, TypeError):
                    continue
                
                try:
                    cantidad = int(cantidad_str) if cantidad_str else 0
                    if cantidad <= 0:
                        continue
                except ValueError:
                    continue
                
                try:
                    precio = float(precio_str) if precio_str else 0
                    if precio <= 0:
                        continue
                except ValueError:
                    continue
                
                try:
                    producto = Producto.objects.get(id=producto_id)
                except Producto.DoesNotExist:
                    continue
                
                subtotal = cantidad * precio
                total_compra += subtotal
                
                CompraDetalle.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio,
                    subtotal=subtotal
                )
                detalles_creados += 1
        
        if detalles_creados == 0:
            compra.delete()
            messages.error(request, '❌ La compra debe tener al menos un producto válido.')
            return render(request, 'compras/crear.html', {
                'productos': productos,
                'proveedores': proveedores,
                'form': CompraForm()
            })
        
        compra.total = total_compra
        compra.save()
        
        messages.success(request, f'✅ Compra #{compra.id} creada exitosamente.')
        return redirect('compras:listar')
    
    productos_json = [{'id': p.id, 'codigo': p.codigo, 'nombre': p.nombre} for p in productos]
    
    return render(request, 'compras/crear.html', {
        'productos': productos,
        'proveedores': proveedores,
        'productos_json': productos_json,
        'today': timezone.now().date(),
        'form': CompraForm()
    })


@login_required
def ver_compra(request, pk):
    """Ver detalle de una compra"""
    compra = get_object_or_404(Compra, pk=pk)
    detalles = compra.detalles.all()
    
    return render(request, 'compras/ver.html', {
        'compra': compra,  # ✅ Corregido el error sintáctico de '_compra'
        'detalles': detalles
    })


@login_required
def recibir_compra(request, pk):
    """Recibir una compra y actualizar el inventario usando lotes"""
    compra = get_object_or_404(Compra, pk=pk)
    
    if compra.estado == 'recibido':
        messages.warning(request, '⚠️ Esta compra ya fue recibida.')
        return redirect('compras:listar')
    
    if request.method == 'POST':
        for detalle in compra.detalles.all():
            producto = detalle.producto
            
            lote = Lote.objects.filter(
                producto=producto,
                estado__in=['activo', 'parcial', 'completado']
            ).order_by('fecha_ingreso').first()
            
            if not lote:
                lote = Lote.objects.create(
                    codigo=f'COMPRA-{producto.codigo}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                    producto=producto,
                    # 🔍 NOTA: Si tu modelo Lote requiere proveedor, cambia 'proveedor_id' 
                    # por el nombre exacto de la columna en tu modelo (ej. 'proveedor_id=compra.proveedor.id')
                    cantidad_total=detalle.cantidad,
                    cantidad_recibida=detalle.cantidad,
                    cantidad_vendida=0,
                    costo_unitario=detalle.precio_unitario,
                    created_by=request.user,
                    estado='completado'
                )
            else:
                lote.cantidad_total += detalle.cantidad
                lote.cantidad_recibida += detalle.cantidad
                lote.save()
        
        compra.estado = 'recibido'
        compra.save()
        
        messages.success(request, f'✅ Compra #{compra.id} recibida e inventario actualizado.')
        return redirect('compras:listar')
    
    return render(request, 'compras/recibir.html', {'compra': compra})


@login_required
def api_ultimo_precio(request, producto_id):
    try:
        try:
            producto_id = int(producto_id)
        except (ValueError, TypeError):
            return JsonResponse({'precio': None, 'error': 'ID inválido', 'success': False})
        
        ultimo_detalle = CompraDetalle.objects.filter(producto_id=producto_id).order_by('-compra__fecha').first()
        
        if ultimo_detalle:
            precio = float(ultimo_detalle.precio_unitario)
        else:
            try:
                producto = Producto.objects.get(id=producto_id)
                precio = float(producto.precio_venta) if producto.precio_venta else 0
            except Producto.DoesNotExist:
                return JsonResponse({'precio': None, 'error': 'No encontrado', 'success': False})
        
        return JsonResponse({'precio': precio, 'success': True})
    except Exception as e:
        return JsonResponse({'precio': None, 'error': str(e), 'success': False})


@login_required
def api_buscar_proveedores(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    proveedores = Proveedor.objects.filter(
        models.Q(nombre__icontains=query) | models.Q(nit__icontains=query)
    )[:10]
    
    results = [{'id': p.id, 'nombre': p.nombre, 'nit': p.nit or 'N/A'} for p in proveedores]
    return JsonResponse({'results': results})