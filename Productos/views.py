from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, FileResponse
from django.db import models
from .models import Producto, Categoria
from .forms import ProductoForm, CategoriaForm
from usuarios.decorators import admin_required, puede_editar_required
import requests
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import io

# ========== VISTAS DE PRODUCTOS ==========

@login_required
def listar_productos(request):
    """
    Lista todos los productos con búsqueda multivariable
    """
    productos = Producto.objects.all().order_by('-id')
    categorias = Categoria.objects.all()
    
    # Búsqueda
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(codigo__icontains=busqueda) |
            Q(marca__icontains=busqueda)
        )
    
    # Filtro por categoría
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
    """
    Crear nuevo producto (solo admin y almacenista)
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
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
    """
    Editar producto existente (solo admin y almacenista)
    """
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
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
    """
    Eliminar producto (solo admin)
    """
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto {nombre} eliminado')
        return redirect('productos:listar')
    
    return render(request, 'productos/eliminar.html', {'producto': producto})


# ========== CARGA MASIVA EXCEL ==========

@login_required
@puede_editar_required
def cargar_productos_excel(request):
    """Carga masiva de productos desde archivo Excel"""
    
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        
        # Validar extensión
        if not archivo.name.endswith(('.xlsx', '.xls')):
            messages.error(request, 'Formato no válido. Use archivos .xlsx o .xls')
            return redirect('productos:carga_masiva')
        
        try:
            df = pd.read_excel(archivo)
            
            # Validar columnas requeridas
            columnas_requeridas = ['codigo', 'nombre', 'precio_venta']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                messages.error(request, f'Faltan columnas: {", ".join(columnas_faltantes)}')
                return redirect('productos:carga_masiva')
            
            creados = 0
            errores = 0
            lista_errores = []
            
            for idx, row in df.iterrows():
                try:
                    if Producto.objects.filter(codigo=row['codigo']).exists():
                        lista_errores.append(f"Fila {idx+2}: Código {row['codigo']} ya existe")
                        errores += 1
                        continue
                    
                    producto = Producto(
                        codigo=row['codigo'],
                        nombre=row['nombre'],
                        marca=row.get('marca', ''),
                        modelo=row.get('modelo', '') if 'modelo' in df.columns else '',
                        stock_actual=int(row.get('stock_actual', 0)),
                        stock_minimo=int(row.get('stock_minimo', 5)),
                        precio_compra=float(row.get('precio_compra', 0)) if pd.notna(row.get('precio_compra', 0)) else None,
                        precio_venta=float(row['precio_venta']),
                        ubicacion=row.get('ubicacion', '') if 'ubicacion' in df.columns else '',
                    )
                    
                    if 'categoria' in df.columns and pd.notna(row.get('categoria')):
                        categoria, _ = Categoria.objects.get_or_create(nombre=row['categoria'])
                        producto.categoria = categoria
                    
                    producto.save()
                    creados += 1
                    
                except Exception as e:
                    lista_errores.append(f"Fila {idx+2}: {str(e)}")
                    errores += 1
            
            if creados > 0:
                messages.success(request, f'✅ {creados} productos importados correctamente')
            if errores > 0:
                messages.warning(request, f'⚠️ {errores} errores. {"; ".join(lista_errores[:5])}')
                
        except Exception as e:
            messages.error(request, f'Error al leer el archivo: {str(e)}')
        
        return redirect('productos:listar')
    
    return render(request, 'productos/carga_masiva.html')


# ========== EXPORTAR EXCEL ==========

@login_required
def exportar_productos_excel(request):
    """Exportar lista de productos a Excel"""
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"
    
    # Estilos
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="3b82f6", end_color="3b82f6", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Encabezados
    headers = ["Código", "Nombre", "Marca", "Modelo", "Categoría", 
               "Stock Actual", "Stock Mínimo", "Estado Stock", 
               "Precio Compra", "Precio Venta", "Ubicación"]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border
    
    # Datos
    productos = Producto.objects.all().order_by('nombre')
    
    for row, producto in enumerate(productos, 2):
        estado_stock = "Crítico" if producto.stock_actual <= producto.stock_minimo else "Normal"
        
        ws.cell(row=row, column=1, value=producto.codigo)
        ws.cell(row=row, column=2, value=producto.nombre)
        ws.cell(row=row, column=3, value=producto.marca or "")
        ws.cell(row=row, column=4, value=producto.modelo or "")
        ws.cell(row=row, column=5, value=producto.categoria.nombre if producto.categoria else "")
        ws.cell(row=row, column=6, value=producto.stock_actual)
        ws.cell(row=row, column=7, value=producto.stock_minimo)
        ws.cell(row=row, column=8, value=estado_stock)
        ws.cell(row=row, column=9, value=float(producto.precio_compra) if producto.precio_compra else 0)
        ws.cell(row=row, column=10, value=float(producto.precio_venta) if producto.precio_venta else 0)
        ws.cell(row=row, column=11, value=producto.ubicacion or "")
        
        for col in range(1, 12):
            ws.cell(row=row, column=col).border = border
    
    # Ajustar ancho de columnas
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 35)
        ws.column_dimensions[col_letter].width = adjusted_width
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=productos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    wb.save(response)
    return response


# ========== REPORTE PDF ==========

@login_required
def reporte_productos_pdf(request):
    """Genera reporte PDF de productos con filtros"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Obtener filtros
    solo_bajo_stock = request.GET.get('solo_bajo_stock')
    
    productos = Producto.objects.all().order_by('nombre')
    if solo_bajo_stock:
        productos = productos.filter(stock_actual__lte=models.F('stock_minimo'))
    
    # Estilos
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], alignment=TA_CENTER, spaceAfter=30)
    
    titulo = Paragraph(f"<b>Reporte de Inventario - SIGI</b><br/><font size='10'>{datetime.now().strftime('%d/%m/%Y %H:%M')}</font>", titulo_style)
    
    # Datos de la tabla
    data = [['Código', 'Producto', 'Marca', 'Stock', 'Stock Mínimo', 'Precio Venta']]
    valor_total = 0
    
    for p in productos:
        estado_stock = "⚠️ Crítico" if p.stock_actual <= p.stock_minimo else "✅ Normal"
        data.append([
            p.codigo, 
            p.nombre, 
            p.marca or '-', 
            f"{p.stock_actual} {estado_stock}",
            str(p.stock_minimo), 
            f"${p.precio_venta:,.2f}"
        ])
        valor_total += p.precio_venta * p.stock_actual
    
    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ]))
    
    resumen = Paragraph(f"<b>Resumen:</b> Total productos: {productos.count()} | Valor inventario: ${valor_total:,.2f}", styles['Normal'])
    
    elementos = [titulo, Spacer(1, 20), tabla, Spacer(1, 20), resumen]
    doc.build(elementos)
    
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'reporte_productos_{datetime.now().strftime("%Y%m%d")}.pdf')


# ========== CONSUMO DE API ==========

@login_required
def consultar_api_productos(request):
    """Consume API de electrodomésticos y tecnología"""
    import requests
    # API de DummyJSON - Categorías: electrodomésticos, laptops, smartphones
    categorias = ["home-decoration", "laptops", "smartphones", "kitchen-accessories"]
    productos_api = []
    
    try:
        for categoria in categorias:
            api_url = f"https://dummyjson.com/products/category/{categoria}"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('products', []):
                productos_api.append({
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'price': item.get('price'),
                    'brand': item.get('brand', 'Tecnología'),
                    'category': item.get('category'),
                    'stock': item.get('stock'),
                    'description': item.get('description'),
                    'thumbnail': item.get('thumbnail'),
                    'rating': item.get('rating', 0)
                })
        
        # Limitar a 15 productos
        productos_api = productos_api[:15]
        
        messages.success(request, f'✅ API consultada. {len(productos_api)} electrodomésticos y tecnología encontrados.')
    except Exception as e:
        messages.error(request, f'❌ Error al consumir API: {str(e)}')
    
    return render(request, 'productos/api_resultados.html', {'productos_api': productos_api})

# ========== VISTAS DE CATEGORÍAS ==========

@login_required
def listar_categorias(request):
    """
    Lista todas las categorías
    """
    categorias = Categoria.objects.all().order_by('nombre')
    
    # Búsqueda
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        categorias = categorias.filter(nombre__icontains=busqueda)
    
    # Paginación
    paginator = Paginator(categorias, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'productos/categorias_lista.html', {
        'categorias': page_obj,
        'busqueda': busqueda
    })


@login_required
def crear_categoria(request):
    """
    Crear nueva categoría
    """
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" creada exitosamente')
            return redirect('productos:categorias')
    else:
        form = CategoriaForm()
    
    return render(request, 'productos/categorias_form.html', {
        'form': form,
        'titulo': 'Nueva Categoría'
    })


@login_required
def editar_categoria(request, pk):
    """
    Editar categoría existente
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f'Categoría "{categoria.nombre}" actualizada')
            return redirect('productos:categorias')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'productos/categorias_form.html', {
        'form': form,
        'titulo': 'Editar Categoría',
        'categoria': categoria
    })


@login_required
def eliminar_categoria(request, pk):
    """
    Eliminar categoría
    """
    categoria = get_object_or_404(Categoria, pk=pk)
    
    if request.method == 'POST':
        nombre = categoria.nombre
        if categoria.producto_set.count() > 0:
            messages.error(request, f'No se puede eliminar "{nombre}" porque tiene productos asociados.')
        else:
            categoria.delete()
            messages.success(request, f'Categoría "{nombre}" eliminada')
        return redirect('productos:categorias')
    
    return render(request, 'productos/categorias_eliminar.html', {'categoria': categoria})