from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # ========== PRODUCTOS ==========
    path('', views.listar_productos, name='listar'),
    path('crear/', views.crear_producto, name='crear'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
    
    # ========== CATEGORÍAS ==========
    path('categorias/', views.listar_categorias, name='categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    
    # ========== PROVEEDORES ==========
    path('proveedores/', views.listar_proveedores, name='proveedores'),
    path('proveedores/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/editar/<int:pk>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/eliminar/<int:pk>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    
    # ========== LOTES (Corregido - usa detalle_lote en lugar de ver_lote) ==========
    path('lotes/', views.listar_lotes, name='listar_lotes'),
    path('lotes/crear/', views.crear_lote, name='crear_lote'),
    path('lotes/<int:pk>/', views.detalle_lote, name='detalle_lote'),  # 🔥 Cambiado de ver_lote a detalle_lote
    path('lotes/<int:pk>/recibir/', views.recibir_lote, name='recibir_lote'),
    
    # ========== SERIALES (NUEVAS RUTAS) ==========
    path('seriales/', views.listar_seriales, name='listar_seriales'),
    path('seriales/<int:pk>/editar/', views.editar_serial, name='editar_serial'),
    
    # ========== BODEGAS ==========
    path('bodegas/', views.listar_bodegas, name='bodegas'),
    path('bodegas/crear/', views.crear_bodega, name='crear_bodega'),
    path('bodegas/editar/<int:pk>/', views.editar_bodega, name='editar_bodega'),
    path('bodegas/eliminar/<int:pk>/', views.eliminar_bodega, name='eliminar_bodega'),
    
    # ========== UTILIDADES ==========
    path('buscar-codigo-barras/', views.buscar_por_codigo_barras, name='buscar_codigo_barras'),
    path('carga-masiva/', views.cargar_productos_excel, name='carga_masiva'),
    path('exportar/excel/', views.exportar_productos_excel, name='exportar_excel'),
    path('reporte/pdf/', views.reporte_productos_pdf, name='reporte_pdf'),
    path('api/consultar/', views.consultar_api_productos, name='consultar_api'),
]