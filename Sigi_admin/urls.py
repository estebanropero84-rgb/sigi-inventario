from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from usuarios import views as usuarios_views  # 🔥 IMPORTAR LAS VISTAS DE USUARIOS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # Redirige a login
    path('dashboard/', include('inventarios.urls')),
    path('productos/', include('Productos.urls')),
    path('movimientos/', include('movimientos.urls')),
    path('compras/', include('compras.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('login/', include('login.urls')),  # ✅ Esto ya incluye todas las URLs de login
    
    # 🔥 AGREGAR LA URL DEL PERFIL
    path('perfil/', usuarios_views.perfil, name='perfil'),
]