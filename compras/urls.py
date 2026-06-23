from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.listar_compras, name='listar'),
    path('crear/', views.crear_compra, name='crear'),
    path('ver/<int:pk>/', views.ver_compra, name='ver'),
    path('recibir/<int:pk>/', views.recibir_compra, name='recibir'),
    
    # ====== APIs ======
    path('api/proveedores/', views.api_buscar_proveedores, name='api_proveedores'),
    path('api/ultimo-precio/<int:producto_id>/', views.api_ultimo_precio, name='api_ultimo_precio'),
]