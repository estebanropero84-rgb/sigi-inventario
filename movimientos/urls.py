from django.urls import path
from . import views

app_name = 'movimientos'

urlpatterns = [
    path('', views.listar_movimientos, name='listar'),
    path('registrar/', views.registrar_movimiento, name='registrar'),
    
    # ====== APIs ======
    path('api/buscar-productos/', views.api_buscar_productos_movimientos, name='api_buscar_productos'),
    path('api/lotes-por-producto/<int:producto_id>/', views.api_lotes_por_producto_movimientos, name='api_lotes_por_producto'),
]