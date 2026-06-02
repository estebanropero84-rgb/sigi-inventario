from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, FileResponse, JsonResponse
from django.db import models
from django.utils import timezone
from datetime import datetime
import io
import requests
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from .models import Producto, Categoria, Proveedor, Lote, ProductoConSerial, Bodega, LogActividad, RecepcionLote
from .forms import ProductoForm, CategoriaForm, ProveedorForm, LoteCompletoForm, RecepcionLoteForm, SerialForm, BodegaForm
from usuarios.decorators import admin_required, puede_editar_required


# ========== FUNCIÓN DE LOGS ==========

def registrar_log(usuario, accion, modelo, objeto_id, objeto_nombre, ip='', detalles=''):
    try:
        LogActividad.objects.create(
            usuario=usuario,
            accion=accion,
            modelo=modelo,
            objeto_id=objeto_id,
            objeto_nombre=objeto_nombre,
            detalles=detalles,
            ip=ip
        )
    except:
        pass


# ========== VISTAS DE PRODUCTOS ==========

@login_required
def listar_productos(request):
    productos = Producto.objects.all().order_by('-id')
    categorias = Categoria.objects.all()
    
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(codigo__icontains=busqueda) |
            Q(marca__icontains=busqueda)
        )
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'busqueda': busqueda,
    }
    return render(request, 'productos/lista.html', context)


@login_required
@puede_editar_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            registrar_log(request.user, 'crear', 'Producto', producto.id, producto.nombre)
            messages.success(request, f'Producto {producto.nombre} creado exitosamente')
            return redirect('productos:listar')
    else:
        form = ProductoForm()
    
    categorias = Categoria.objects.all()
    return render(request, 'productos/form.html', {
        'form': form, 
        'titulo': 'Nuevo Producto',
        'categorias': categorias
    })


@login_required
@puede_editar_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            registrar_log(request.user, 'editar', 'Producto', producto.id, producto.nombre)
            messages.success(request, f'Producto {producto.nombre} actualizado')
            return redirect('productos:listar')
    else:
        form = ProductoForm(instance=producto)
    
    categorias = Categoria.objects.all()
    return render(request, 'productos/form.html', {
        'form': form, 
        'titulo': 'Editar Producto', 
        'producto': producto,
        'categorias': categorias
    })


@login_required
@admin_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre = producto.nombre
        registrar_log(request.user, 'eliminar', 'Producto', producto.id, nombre)
        producto.delete()
        messages.success(request, f'Producto {nombre} eliminado')
        return redirect('productos:listar')
    
    return render(request, 'productos/eliminar.html', {'producto': producto})


# ========== CARGA MASIVA EXCEL ==========

@login_required
def cargar_productos_excel(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        
        if not archivo.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Formato no válido. Use archivos .xlsx o .xls')
            return redirect('productos:carga_masiva')
        
        try:
            df = pd.read_excel(archivo)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
            
            columnas_requeridas = ['codigo', 'nombre', 'precio_venta']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                messages.error(request, f'Faltan columnas: {", ".join(columnas_faltantes)}')
                return redirect('productos:carga_masiva')
            
            creados = 0
            for idx, row in df.iterrows():
                if not Producto.objects.filter(codigo=str(row['codigo'])).exists():
                    producto = Producto(
                        codigo=str(row['codigo']),
                        nombre=str(row['nombre']),
                        precio_venta=float(row['precio_venta']),
                    )
                    producto.save()
                    creados += 1
            
            messages.success(request, f'✅ {creados} productos importados correctamente')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('productos:listar')
    
    return render(request, 'productos/carga_masiva.html')


# ========== EXPORTAR EXCEL ==========

@login_required
def exportar_productos_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"
    
    headers = ["Código", "Nombre", "Marca", "Stock", "Precio Venta"]
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)
        ws.cell(row=1, column=col).font = Font(bold=True)
    
    productos = Producto.objects.all().order_by('nombre')
    for row, producto in enumerate(productos, 2):
        ws.cell(row=row, column=1, value=producto.codigo)
        ws.cell(row=row, column=2, value=producto.nombre)
        ws.cell(row=row, column=3, value=producto.marca or "")
        ws.cell(row=row, column=4, value=producto.stock_actual)
        ws.cell(row=row, column=5, value=float(producto.precio_venta))
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=productos_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


# ========== REPORTE PDF ==========

@login_required
def reporte_productos_pdf(request):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    
    productos = Producto.objects.all().order_by('nombre')
    
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=30)
    titulo = Paragraph(f"<b>Reporte de Inventario - SIGI</b><br/><font size='10'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</font>", titulo_style)
    
    data = [['Código', 'Producto', 'Marca', 'Stock', 'Stock Mínimo', 'Precio Venta']]
    valor_total = 0
    
    for p in productos:
        estado_stock = "⚠️ Crítico" if p.stock_actual <= p.stock_minimo else "✅ Normal"
        data.append([
            p.codigo, p.nombre[:30] if p.nombre else '-', 
            p.marca[:20] if p.marca else '-', 
            f"{p.stock_actual} {estado_stock}",
            str(p.stock_minimo), f"${p.precio_venta:,.2f}"
        ])
        valor_total += float(p.precio_venta or 0) * int(p.stock_actual or 0)
    
    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    resumen = Paragraph(f"<b>Resumen:</b> Total: {productos.count()} | Valor: ${valor_total:,.2f}", styles['Normal'])
    doc.build([titulo, Spacer(1, 20), tabla, Spacer(1, 20), resumen])
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'reporte_productos_{datetime.now().strftime("%Y%m%d")}.pdf')


# ========== CONSUMO DE API ==========

@login_required
def consultar_api_productos(request):
    api_url = "https://api.escuelajs.co/api/v1/products"
    productos_api = []
    
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        for item in data[:15]:
            productos_api.append({
                'id': item.get('id'),
                'title': item.get('title', 'Sin título'),
                'price': item.get('price', 0),
                'category': item.get('category', {}).get('name', 'General'),
            })
        messages.success(request, f'✅ {len(productos_api)} productos encontrados')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        productos_api = [
            {'id': 1, 'title': 'Lavadora LG', 'price': 850, 'category': 'Electrodomésticos'},
            {'id': 2, 'title': 'Refrigerador Samsung', 'price': 1200, 'category': 'Electrodomésticos'},
        ]
    
    return render(request, 'productos/api_resultados.html', {'productos_api': productos_api})


# ========== VISTAS DE CATEGORÍAS ==========

@login_required
def listar_categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'productos/categorias_lista.html', {'categorias': categorias})

@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada')
            return redirect('productos:categorias')
    else:
        form = CategoriaForm()
    return render(request, 'productos/categorias_form.html', {'form': form, 'titulo': 'Nueva Categoría'})

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada')
            return redirect('productos:categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'productos/categorias_form.html', {'form': form, 'titulo': 'Editar Categoría', 'categoria': categoria})

@login_required
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = categoria.nombre
        if categoria.producto_set.count() > 0:
            messages.error(request, f'No se puede eliminar "{nombre}" porque tiene productos asociados')
        else:
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada')
        return redirect('productos:categorias')
    return render(request, 'productos/categorias_eliminar.html', {'categoria': categoria})


# ========== VISTAS DE PROVEEDORES ==========

@login_required
def listar_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(request, 'productos/proveedores_lista.html', {'proveedores': proveedores})

@login_required
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor {proveedor.nombre} creado')
            return redirect('productos:proveedores')
    else:
        form = ProveedorForm()
    return render(request, 'productos/proveedores_form.html', {'form': form, 'titulo': 'Nuevo Proveedor'})

@login_required
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proveedor {proveedor.nombre} actualizado')
            return redirect('productos:proveedores')
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'productos/proveedores_form.html', {'form': form, 'titulo': 'Editar Proveedor', 'proveedor': proveedor})

@login_required
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        nombre = proveedor.nombre
        if proveedor.lotes.count() > 0:
            messages.error(request, f'No se puede eliminar "{nombre}" porque tiene lotes asociados')
        else:
            proveedor.delete()
            messages.success(request, f'Proveedor {nombre} eliminado')
        return redirect('productos:proveedores')
    return render(request, 'productos/proveedores_eliminar.html', {'proveedor': proveedor})


# ========== VISTAS DE LOTES (CORREGIDAS) ==========

@login_required
def listar_lotes(request):
    """Lista de lotes"""
    lotes = Lote.objects.all().order_by('-created_at')
    
    estado = request.GET.get('estado')
    if estado:
        lotes = lotes.filter(estado=estado)
    
    paginator = Paginator(lotes, 20)
    page = request.GET.get('page')
    lotes = paginator.get_page(page)
    
    return render(request, 'productos/lotes_lista.html', {
        'lotes': lotes,
        'estado_actual': estado,
    })


@login_required
def crear_lote(request):
    """Crear nuevo lote"""
    if request.method == 'POST':
        form = LoteCompletoForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.created_by = request.user
            lote.cantidad_recibida = 0
            lote.save()
            registrar_log(request.user, 'crear', 'Lote', lote.id, lote.codigo)
            messages.success(request, f'✅ Lote {lote.codigo} creado exitosamente')
            return redirect('productos:detalle_lote', pk=lote.id)
    else:
        form = LoteCompletoForm()
    
    return render(request, 'productos/lote_form.html', {
        'form': form,
        'titulo': 'Crear Lote'
    })


@login_required
def detalle_lote(request, pk):
    """Detalle del lote"""
    lote = get_object_or_404(Lote, pk=pk)
    seriales = lote.productos.all()
    
    resumen = {
        'total': seriales.count(),
        'disponible': seriales.filter(estado='disponible').count(),
        'vendido': seriales.filter(estado='vendido').count(),
        'danado': seriales.filter(estado='danado').count(),
        'devuelto': seriales.filter(estado='devuelto').count(),
        'reservado': seriales.filter(estado='reservado').count(),
    }
    
    return render(request, 'productos/lote_detalle.html', {
        'lote': lote,
        'seriales': seriales,
        'resumen': resumen,
        'porcentaje': lote.porcentaje_recibido,
    })


@login_required
def recibir_lote(request, pk):
    """Recibir productos del lote con seriales"""
    lote = get_object_or_404(Lote, pk=pk)
    
    if lote.estado == 'completado':
        messages.warning(request, 'Este lote ya está completado')
        return redirect('productos:detalle_lote', pk=lote.id)
    
    if request.method == 'POST':
        form = RecepcionLoteForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            seriales_text = form.cleaned_data['seriales']
            notas = form.cleaned_data['notas']
            
            seriales_lista = [s.strip() for s in seriales_text.strip().split('\n') if s.strip()]
            
            # Validaciones
            if len(seriales_lista) != cantidad:
                messages.error(request, f'La cantidad de seriales ({len(seriales_lista)}) no coincide con la cantidad indicada ({cantidad})')
                return render(request, 'productos/lote_recibir.html', {'form': form, 'lote': lote})
            
            if lote.cantidad_recibida + cantidad > lote.cantidad_total:
                messages.error(request, f'No puedes recibir más de {lote.restante} unidades. Restante: {lote.restante}')
                return render(request, 'productos/lote_recibir.html', {'form': form, 'lote': lote})
            
            # Verificar seriales duplicados
            if len(seriales_lista) != len(set(seriales_lista)):
                messages.error(request, 'Hay seriales duplicados en la lista')
                return render(request, 'productos/lote_recibir.html', {'form': form, 'lote': lote})
            
            # Verificar seriales ya existentes
            existentes = ProductoConSerial.objects.filter(serial__in=seriales_lista)
            if existentes.exists():
                existentes_str = ', '.join(existentes.values_list('serial', flat=True)[:5])
                messages.error(request, f'Los siguientes seriales ya existen: {existentes_str}')
                return render(request, 'productos/lote_recibir.html', {'form': form, 'lote': lote})
            
            # Crear seriales
            creados = 0
            for serial in seriales_lista:
                ProductoConSerial.objects.create(
                    serial=serial,
                    producto_base=lote.producto,
                    lote=lote,
                    estado='disponible',
                    notas=notas
                )
                creados += 1
            
            # Actualizar lote
            lote.cantidad_recibida += cantidad
            if lote.cantidad_recibida >= lote.cantidad_total:
                lote.estado = 'completado'
                lote.fecha_entrega = timezone.now().date()
            else:
                lote.estado = 'parcial'
            lote.save()
            
            # Registrar recepción
            RecepcionLote.objects.create(
                lote=lote,
                cantidad=cantidad,
                seriales=seriales_text,
                recibido_por=request.user,
                notas=notas
            )
            
            # Actualizar stock del producto
            producto = lote.producto
            producto.stock_actual += cantidad
            producto.save()
            
            registrar_log(request.user, 'recibir', 'Lote', lote.id, f'{cantidad} unidades - {lote.codigo}')
            messages.success(request, f'✅ Lote recibido: {cantidad} productos con seriales')
            return redirect('productos:detalle_lote', pk=lote.id)
    else:
        form = RecepcionLoteForm()
    
    return render(request, 'productos/lote_recibir.html', {
        'form': form,
        'lote': lote
    })


# ========== VISTAS DE SERIALES ==========

@login_required
def listar_seriales(request):
    """Lista de seriales"""
    seriales = ProductoConSerial.objects.all().order_by('serial')
    
    estado = request.GET.get('estado')
    if estado:
        seriales = seriales.filter(estado=estado)
    
    producto_id = request.GET.get('producto')
    if producto_id:
        seriales = seriales.filter(producto_base_id=producto_id)
    
    busqueda = request.GET.get('q')
    if busqueda:
        seriales = seriales.filter(serial__icontains=busqueda)
    
    paginator = Paginator(seriales, 50)
    page = request.GET.get('page')
    seriales = paginator.get_page(page)
    
    productos = Producto.objects.all().order_by('nombre')
    
    return render(request, 'productos/seriales_lista.html', {
        'seriales': seriales,
        'productos': productos,
        'estado_actual': estado,
    })


@login_required
def editar_serial(request, pk):
    """Editar estado de un serial"""
    serial = get_object_or_404(ProductoConSerial, pk=pk)
    
    if request.method == 'POST':
        form = SerialForm(request.POST, instance=serial)
        if form.is_valid():
            form.save()
            registrar_log(request.user, 'editar', 'Serial', serial.id, serial.serial)
            messages.success(request, f'✅ Serial {serial.serial} actualizado a {serial.get_estado_display()}')
            return redirect('productos:listar_seriales')
    else:
        form = SerialForm(instance=serial)
    
    return render(request, 'productos/serial_form.html', {
        'form': form,
        'serial': serial
    })


# ========== VISTAS DE BODEGAS ==========

@login_required
def listar_bodegas(request):
    bodegas = Bodega.objects.all().order_by('nombre')
    return render(request, 'productos/bodegas_lista.html', {'bodegas': bodegas})

@login_required
def crear_bodega(request):
    if request.method == 'POST':
        form = BodegaForm(request.POST)
        if form.is_valid():
            bodega = form.save()
            messages.success(request, f'Bodega {bodega.nombre} creada')
            return redirect('productos:bodegas')
    else:
        form = BodegaForm()
    return render(request, 'productos/bodegas_form.html', {'form': form, 'titulo': 'Nueva Bodega'})

@login_required
def editar_bodega(request, pk):
    bodega = get_object_or_404(Bodega, pk=pk)
    if request.method == 'POST':
        form = BodegaForm(request.POST, instance=bodega)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bodega {bodega.nombre} actualizada')
            return redirect('productos:bodegas')
    else:
        form = BodegaForm(instance=bodega)
    return render(request, 'productos/bodegas_form.html', {'form': form, 'titulo': 'Editar Bodega', 'bodega': bodega})

@login_required
def eliminar_bodega(request, pk):
    bodega = get_object_or_404(Bodega, pk=pk)
    if request.method == 'POST':
        nombre = bodega.nombre
        if bodega.productos.count() > 0:
            messages.error(request, f'No se puede eliminar "{nombre}" porque tiene productos asociados')
        else:
            bodega.delete()
            messages.success(request, f'Bodega {nombre} eliminada')
        return redirect('productos:bodegas')
    return render(request, 'productos/bodegas_eliminar.html', {'bodega': bodega})


# ========== ESCÁNER CÓDIGO DE BARRAS ==========

@login_required
def buscar_por_codigo_barras(request):
    """Busca un producto por su código de barras (API para escáner)"""
    codigo = request.GET.get('codigo', '').strip()
    
    if not codigo:
        return JsonResponse({'error': 'No se proporcionó código'}, status=400)
    
    try:
        producto = Producto.objects.filter(
            Q(codigo_barras=codigo) | Q(codigo=codigo)
        ).first()
        
        if producto:
            return JsonResponse({
                'success': True,
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'marca': producto.marca,
                'stock_actual': producto.stock_actual,
                'precio_venta': float(producto.precio_venta),
            })
        else:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)