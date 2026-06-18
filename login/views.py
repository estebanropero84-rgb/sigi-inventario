from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from datetime import datetime
import traceback
import sys

# === LOG DE INICIO ===
print("=" * 70)
print("📂 CARGANDO login/views.py (SIN LOGS)")
print(f"🐍 Python version: {sys.version}")
print("=" * 70)

def get_client_ip(request):
    """Obtiene la IP real del cliente"""
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except Exception as e:
        print(f"⚠️ Error obteniendo IP: {e}")
        return '0.0.0.0'

# ⚠️ FUNCIÓN DE LOG DESACTIVADA - NO USA BASE DE DATOS
def registrar_log(usuario, accion, ip, detalles=''):
    """Registro de seguridad DESACTIVADO para evitar errores en Render"""
    print(f"⚠️ LOG DESACTIVADO: {accion} - Usuario: {usuario} - IP: {ip}")
    return True  # Siempre retorna éxito sin guardar en BD

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def login_view(request):
    """Vista de login simplificada (sin rate limiting para pruebas)"""
    
    print("=" * 70)
    print("🔐 INICIO DE LOGIN VIEW (SIN LOGS)")
    print("=" * 70)
    
    try:
        print(f"📌 URL: {request.path}")
        print(f"📌 Método HTTP: {request.method}")
        print(f"📌 Usuario autenticado: {request.user.is_authenticated}")
        
        ip = get_client_ip(request)
        print(f"📍 IP del cliente: {ip}")
        
        if request.user.is_authenticated:
            print("✅ Usuario ya autenticado, redirigiendo a dashboard")
            return redirect('inventarios:dashboard')
        
        if request.method == 'POST':
            print("📥 Procesando POST de login")
            
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            print(f"👤 Username recibido: '{username}'")
            print(f"🔑 Password: {'***' if password else 'No recibida'}")
            
            if not username or not password:
                print("⚠️ Username o password vacíos")
                messages.error(request, 'Usuario y contraseña son requeridos')
                return render(request, 'login.html')
            
            print("🔍 Autenticando usuario...")
            
            try:
                user = authenticate(request, username=username, password=password)
                print(f"👤 Resultado autenticación: {'✅ Éxito' if user else '❌ Falló'}")
                
                if user:
                    print(f"   - ID: {user.id}")
                    print(f"   - is_active: {user.is_active}")
                    print(f"   - is_superuser: {user.is_superuser}")
            except Exception as e:
                print(f"❌ Error en authenticate(): {str(e)}")
                traceback.print_exc()
                messages.error(request, 'Error en autenticación. Contacte al administrador.')
                return render(request, 'login.html')
            
            if user is not None:
                if user.is_active:
                    print("✅ Usuario activo - Iniciando sesión...")
                    
                    try:
                        # Registrar log (desactivado)
                        registrar_log(username, 'login_exito', ip, 'Login exitoso')
                    except:
                        pass
                    
                    try:
                        login(request, user)
                        print(f"🔐 Usuario {user.username} logueado exitosamente")
                        messages.success(request, f'Bienvenido {user.username}')
                        return redirect('inventarios:dashboard')
                    except Exception as e:
                        print(f"❌ Error en login(): {str(e)}")
                        traceback.print_exc()
                        messages.error(request, f'Error iniciando sesión')
                        return render(request, 'login.html')
                else:
                    print("⚠️ Usuario inactivo")
                    messages.error(request, 'Usuario desactivado. Contacte al administrador.')
            else:
                print("❌ Credenciales inválidas")
                messages.error(request, 'Usuario o contraseña incorrectos')
            
            return render(request, 'login.html')
        
        # GET - Mostrar formulario
        print("📄 Mostrando formulario de login (GET)")
        return render(request, 'login.html')
        
    except Exception as e:
        print("=" * 70)
        print("❌❌❌ ERROR CRÍTICO EN LOGIN_VIEW ❌❌❌")
        print("=" * 70)
        print(f"Mensaje: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        print("Stack trace:")
        traceback.print_exc()
        print("=" * 70)
        
        messages.error(request, 'Error interno del servidor. Contacte al administrador.')
        return render(request, 'login.html')


def logout_view(request):
    print("=" * 70)
    print("🚪 LOGOUT VIEW")
    print("=" * 70)
    
    try:
        ip = get_client_ip(request)
        print(f"📍 IP: {ip}")
        
        if request.user.is_authenticated:
            username = request.user.username
            print(f"👤 Cerrando sesión de: {username}")
            registrar_log(username, 'logout', ip, 'Cierre de sesión')
        else:
            print("ℹ️ No hay usuario autenticado")
        
        logout(request)
        print("✅ Logout completado")
        messages.info(request, 'Sesión cerrada correctamente')
        
    except Exception as e:
        print(f"❌ Error en logout: {str(e)}")
        traceback.print_exc()
    
    return redirect('login')