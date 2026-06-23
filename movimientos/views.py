from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Movimiento
from Productos.models import Producto, Lote
from .forms import MovimientoForm
import re

# Obtener el modelo de usuario configurado
User = get_user_model()


@login_required
def listar_movimientos(request):
    """Lista de movimientos con filtros"""
    movimientos = Movimiento.objects.all().order_by('-created_at')
    
    # ====== FILTROS ======
    buscar = request.GET.get('buscar')
    if buscar:
        movimientos = movimientos.filter(producto__nombre__icontains=buscar)
    
    tipo = request.GET.get('tipo')
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    
    motivo = request.GET.get('motivo')
    if motivo:
        movimientos = movimientos.filter(motivo=motivo)
    
    fecha_desde = request.GET.get('fecha_desde')
    if fecha_desde:
        movimientos = movimientos.filter(created_at__date__gte=fecha_desde)
    
    fecha_hasta = request.GET.get('fecha_hasta')
    if fecha_hasta:
        movimientos = movimientos.filter(created_at__date__lte=fecha_hasta)
    
    # ====== ESTADÍSTICAS ======
    total_movimientos = movimientos.count()
    total_entradas = movimientos.filter(tipo='entrada').count()
    total_salidas = movimientos.filter(tipo='salida').count()
    
    # ====== PAGINACIÓN ======
    from django.core.paginator import Paginator
    paginator = Paginator(movimientos, 20)
    page = request.GET.get('page')
    movimientos_page = paginator.get_page(page)
    
    context = {
        'movimientos': movimientos_page,
        'total_movimientos': total_movimientos,
        'total_entradas': total_entradas,
        'total_salidas': total_salidas,
    }
    return render(request, 'movimientos/movimientos_lista.html', context)


@login_required
def registrar_movimiento(request):
    """Registrar movimiento de inventario (por serial)"""
    
    # ====== PRODUCTOS PARA EL FORMULARIO ======
    productos = Producto.objects.all().order_by('nombre')
    lotes_disponibles = Lote.objects.filter(
        cantidad_recibida__gt=models.F('cantidad_vendida')
    ).order_by('-created_at')
    
    # ====== PREFILL DESDE GET ======
    producto_id = request.GET.get('producto')
    tipo_predefinido = request.GET.get('tipo')
    
    producto_seleccionado = None
    if producto_id:
        producto_seleccionado = get_object_or_404(Producto, pk=producto_id)
    
    # ====== PROCESAR POST ======
    if request.method == 'POST':
        # Verificar si es AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        producto_id = request.POST.get('producto')
        tipo = request.POST.get('tipo')
        serial = request.POST.get('serial', '').strip()
        lote_id = request.POST.get('lote')
        motivo = request.POST.get('motivo', '')
        observacion = request.POST.get('observacion', '')
        
        # ====== VALIDACIONES ======
        if not producto_id:
            error = 'Por favor selecciona un producto.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, f'❌ {error}')
            return redirect('movimientos:registrar')
        
        if not tipo:
            error = 'Por favor selecciona un tipo de movimiento.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, f'❌ {error}')
            return redirect('movimientos:registrar')
        
        if not serial:
            error = 'Por favor ingresa el serial del producto.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, f'❌ {error}')
            return redirect('movimientos:registrar')
        
        # Validar formato del serial
        if not re.match(r'^[A-Za-z0-9\-_]{3,50}$', serial):
            error = 'Formato de serial inválido. Usa letras, números, guiones o guiones bajos.'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)
            messages.error(request, f'❌ {error}')
            return redirect('movimientos:registrar')
        
        # Obtener producto
        producto = get_object_or_404(Producto, pk=producto_id)
        
        # Obtener lote (opcional)
        lote = None
        if lote_id:
            lote = get_object_or_404(Lote, pk=lote_id)
            # Verificar que el lote pertenezca al producto
            if lote.producto.id != producto.id:
                error = 'El lote seleccionado no pertenece a este producto.'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, f'❌ {error}')
                return redirect('movimientos:registrar')
        
        # ====== CALCULAR STOCK ======
        stock_actual = producto.stock_total()
        cantidad = 1  # Siempre 1 por serial
        
        # ====== PROCESAR SEGÚN TIPO ======
        if tipo == 'entrada':
            # Entrada: aumentar stock
            stock_nuevo = stock_actual + cantidad
            
            # Crear o actualizar lote si no se seleccionó uno
            if not lote:
                # Buscar un lote activo o crear uno
                lote = Lote.objects.filter(
                    producto=producto,
                    estado__in=['completado', 'parcial', 'activo']
                ).order_by('fecha_ingreso').first()
                
                if not lote:
                    # Crear lote automático
                    lote = Lote.objects.create(
                        codigo=f'AUTO-{producto.codigo}-{timezone.now().strftime("%Y%m%d%H%M%S")}',
                        producto=producto,
                        cantidad_total=0,
                        cantidad_recibida=0,
                        cantidad_vendida=0,
                        costo_unitario=0,
                        created_by=request.user,
                        estado='activo'
                    )
            
            # Actualizar lote
            lote.cantidad_recibida += cantidad
            lote.cantidad_total = max(lote.cantidad_total, lote.cantidad_recibida)
            lote.save()
            
        elif tipo in ['salida', 'devolucion']:
            # Salida/Devolución: disminuir stock
            if cantidad > stock_actual:
                error = f'No hay suficiente stock. Disponible: {stock_actual}'
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error}, status=400)
                messages.error(request, f'❌ {error}')
                return render(request, 'movimientos/movimiento_registrar.html', {
                    'productos': productos,
                    'producto_seleccionado': producto_seleccionado,
                    'tipo_predefinido': tipo_predefinido,
                    'lotes_disponibles': lotes_disponibles,
                    'form': MovimientoForm()
                })
            
            stock_nuevo = stock_actual - cantidad
            
            # Si no se seleccionó lote, buscar uno con stock disponible (FIFO)
            if not lote:
                lote = Lote.objects.filter(
                    producto=producto,
                    cantidad_recibida__gt=models.F('cantidad_vendida')
                ).order_by('fecha_ingreso').first()
                
                if not lote:
                    error = 'No hay lotes disponibles con stock para este producto.'
                    if is_ajax:
                        return JsonResponse({'success': False, 'error': error}, status=400)
                    messages.error(request, f'❌ {error}')
                    return render(request, 'movimientos/movimiento_registrar.html', {
                        'productos': productos,
                        'producto_seleccionado': producto_seleccionado,
                        'tipo_predefinido': tipo_predefinido,
                        'lotes_disponibles': lotes_disponibles,
                        'form': MovimientoForm()
                    })
            
            # Descontar del lote
            lote.cantidad_vendida += cantidad
            lote.actualizar_estado()
            
            # Actualizar seriales si existen
            seriales_disponibles = producto.unidades.filter(
                lote=lote,
                estado='disponible'
            )
            if seriales_disponibles.exists():
                # Tomar el primer serial disponible
                serial_obj = seriales_disponibles.first()
                if tipo == 'salida':
                    serial_obj.estado = 'vendido'
                elif tipo == 'devolucion':
                    serial_obj.estado = 'devuelto'
                serial_obj.save()
        
        else:
            # Ajuste u otros tipos
            stock_nuevo = stock_actual
        
        # ====== CREAR MOVIMIENTO ======
        movimiento = Movimiento.objects.create(
            producto=producto,
            lote=lote,
            tipo=tipo,
            cantidad=cantidad,
            serial=serial,
            stock_anterior=stock_actual,
            stock_nuevo=stock_nuevo,
            motivo=motivo,
            observacion=observacion,
            usuario=request.user
        )
        
        # ====== RESPUESTA ======
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f'✅ Movimiento registrado: {movimiento.get_tipo_display()} de {producto.nombre}',
                'redirect': reverse('movimientos:listar')
            })
        
        messages.success(request, f'✅ Movimiento registrado: {movimiento.get_tipo_display()} de {producto.nombre}')
        return redirect('movimientos:listar')
    
    # ====== GET - MOSTRAR FORMULARIO ======
    return render(request, 'movimientos/movimiento_registrar.html', {
        'productos': productos,
        'producto_seleccionado': producto_seleccionado,
        'tipo_predefinido': tipo_predefinido,
        'lotes_disponibles': lotes_disponibles,
        'form': MovimientoForm()
    })


@login_required
def api_buscar_productos_movimientos(request):
    """API para buscar productos (usado en el formulario de movimientos)"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    productos = Producto.objects.filter(
        models.Q(nombre__icontains=query) |
        models.Q(codigo__icontains=query)
    )[:10]
    
    results = [{
        'id': p.id,
        'nombre': p.nombre,
        'codigo': p.codigo,
        'stock': p.stock_total()
    } for p in productos]
    
    return JsonResponse({'results': results})


@login_required
def api_lotes_por_producto_movimientos(request, producto_id):
    """API para obtener lotes de un producto"""
    try:
        producto = get_object_or_404(Producto, pk=producto_id)
        lotes = Lote.objects.filter(
            producto=producto,
            cantidad_recibida__gt=models.F('cantidad_vendida')
        ).order_by('-created_at')
        
        data = {
            'lotes': [{
                'id': lote.id,
                'codigo': lote.codigo,
                'producto': lote.producto.nombre,
                'disponible': lote.disponible
            } for lote in lotes]
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)