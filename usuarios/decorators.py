from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """
    Decorador que permite acceso SOLO a administradores
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.es_admin:
            messages.error(request, 'No tienes permisos de administrador')
            return redirect('inventarios:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def almacenista_required(view_func):
    """
    Decorador que permite acceso a administradores y almacenistas
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.es_admin or request.user.es_almacenista):
            messages.error(request, 'No tienes permisos de almacenista')
            return redirect('inventarios:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def puede_editar_required(view_func):
    """
    Decorador que permite acceso a usuarios que pueden editar productos
    (Admin y Almacenista)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.es_admin or request.user.es_almacenista):
            messages.error(request, 'No tienes permisos para editar productos')
            return redirect('inventarios:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def consultor_required(view_func):
    """
    Decorador que permite acceso a consultores (solo lectura)
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol not in ['admin', 'almacenista', 'consultor']:
            messages.error(request, 'No tienes permiso para acceder')
            return redirect('inventarios:dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view