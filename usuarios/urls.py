from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.listar_usuarios, name='listar'),
    path('crear/', views.crear_usuario, name='crear'),
    path('editar/<int:pk>/', views.editar_usuario, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar'),
    path('logs/', views.logs_seguridad, name='logs_seguridad'),  # ✅ Este es el nombre correcto
    path('perfil/', views.perfil, name='perfil'),
]