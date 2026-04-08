from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),  # Redirige a login por defecto
    path('dashboard/', include('inventarios.urls')),
    path('productos/', include('Productos.urls')),
    path('movimientos/', include('movimientos.urls')),
    path('compras/', include('compras.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('login/', include('login.urls')),
]