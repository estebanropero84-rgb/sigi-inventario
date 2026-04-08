from django.urls import path
from . import views

app_name = 'movimientos'

urlpatterns = [
    path('', views.listar_movimientos, name='listar'),
    path('registrar/', views.registrar_movimiento, name='registrar'),
]