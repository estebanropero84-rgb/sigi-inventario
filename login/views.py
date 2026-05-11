from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from usuarios.models import SeguridadLog
from datetime import datetime

def get_client_ip(request):
    """Obtiene la IP real del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def registrar_log(usuario, accion, ip, detalles=''):
    """Registra eventos de seguridad"""
    try:
        SeguridadLog.objects.create(
            usuario=usuario[:150] if usuario else None,
            ip=ip,
            accion=accion,
            detalles=detalles
        )
    except:
        pass

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
@ratelimit(key='ip', rate='3/m', method='POST')
def login_view(request):
    """Vista de login con rate limiting y seguridad mejorada"""
    
    ip = get_client_ip(request)
    
    # Verificar si está bloqueado temporalmente
    bloqueado = cache.get(f'bloqueado_{ip}')
    if bloqueado:
        messages.error(request, f'Demasiados intentos. Intenta de nuevo en {bloqueado} minutos.')
        return render(request, 'login.html')
    
    if request.user.is_authenticated:
        return redirect('inventarios:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Contar intentos fallidos recientes
        intentos_key = f'intentos_{ip}'
        intentos = cache.get(intentos_key, 0)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login exitoso
            if user.is_active:
                registrar_log(username, 'login_exito', ip, 'Login exitoso')
                # Limpiar intentos fallidos
                cache.delete(intentos_key)
                request.session.flush()
                login(request, user)
                messages.success(request, f'Bienvenido {user.username}')
                return redirect('inventarios:dashboard')
            else:
                registrar_log(username, 'login_fallo', ip, 'Usuario inactivo')
                messages.error(request, 'Usuario desactivado. Contacte al administrador.')
        else:
            # Login fallido
            intentos += 1
            cache.set(intentos_key, intentos, 300)  # 5 minutos
            
            registrar_log(username, 'login_fallo', ip, f'Contraseña incorrecta (intento {intentos})')
            
            # Si hay 5 intentos fallidos, bloquear por 15 minutos
            if intentos >= 5:
                cache.set(f'bloqueado_{ip}', 15, 900)  # 15 minutos
                messages.error(request, 'Demasiados intentos fallidos. Intenta de nuevo en 15 minutos.')
            else:
                messages.error(request, f'Usuario o contraseña incorrectos. Intentos restantes: {5 - intentos}')
        
        return render(request, 'login.html')
    
    return render(request, 'login.html')


def logout_view(request):
    ip = get_client_ip(request)
    if request.user.is_authenticated:
        registrar_log(request.user.username, 'logout', ip, 'Cierre de sesión')
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')