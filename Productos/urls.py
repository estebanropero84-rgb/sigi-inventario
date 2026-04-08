from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    # Productos
    path('', views.listar_productos, name='listar'),
    path('crear/', views.crear_producto, name='crear'),
    path('editar/<int:pk>/', views.editar_producto, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_producto, name='eliminar'),
    
    # Categorías
    path('categorias/', views.listar_categorias, name='categorias'),
    path('categorias/crear/', views.crear_categoria, name='crear_categoria'),
    path('categorias/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/eliminar/<int:pk>/', views.eliminar_categoria, name='eliminar_categoria'),
    path('carga-masiva/', views.cargar_productos_excel, name='carga_masiva'),
    path('exportar/excel/', views.exportar_productos_excel, name='exportar_excel'),
    path('api/consultar/', views.consultar_api_productos, name='consultar_api'),
    path('reporte/pdf/', views.reporte_productos_pdf, name='reporte_pdf'),
]
