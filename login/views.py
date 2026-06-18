from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from usuarios.models import SeguridadLog
from datetime import datetime
import traceback
import sys

# === LOG DE INICIO ===
print("=" * 70)
print("📂 CARGANDO login/views.py")
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

def registrar_log(usuario, accion, ip, detalles=''):
    """Registra eventos de seguridad con manejo de errores"""
    try:
        print(f"📝 Registrando log: {accion} - Usuario: {usuario} - IP: {ip}")
        log = SeguridadLog.objects.create(
            usuario=usuario[:150] if usuario else None,
            ip=ip,
            accion=accion,
            detalles=detalles
        )
        print(f"✅ Log registrado exitosamente (ID: {log.id})")
        return True
    except Exception as e:
        print(f"❌ Error registrando log: {str(e)}")
        print(f"   Stack: {traceback.format_exc()}")
        return False

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@ratelimit(key='ip', rate='10/h', method='POST', block=True)
@ratelimit(key='ip', rate='3/m', method='POST')
def login_view(request):
    """Vista de login con rate limiting y seguridad mejorada"""
    
    print("=" * 70)
    print("🔐 INICIO DE LOGIN VIEW")
    print("=" * 70)
    
    try:
        print(f"📌 URL: {request.path}")
        print(f"📌 Método HTTP: {request.method}")
        print(f"📌 Usuario autenticado: {request.user.is_authenticated}")
        
        ip = get_client_ip(request)
        print(f"📍 IP del cliente: {ip}")
        
        # Verificar si está bloqueado temporalmente
        try:
            bloqueado = cache.get(f'bloqueado_{ip}')
            if bloqueado:
                print(f"⛔ IP bloqueada por {bloqueado} minutos")
                messages.error(request, f'Demasiados intentos. Intenta de nuevo en {bloqueado} minutos.')
                return render(request, 'login.html')
        except Exception as e:
            print(f"⚠️ Error verificando bloqueo en caché: {e}")
        
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
            
            # Contar intentos fallidos
            try:
                intentos_key = f'intentos_{ip}'
                intentos = cache.get(intentos_key, 0)
                print(f"📊 Intentos fallidos previos: {intentos}")
            except Exception as e:
                print(f"⚠️ Error accediendo a caché: {e}")
                intentos = 0
            
            # Autenticar
            print("🔍 Autenticando usuario...")
            try:
                user = authenticate(request, username=username, password=password)
                print(f"👤 Resultado autenticación: {'✅ Éxito' if user else '❌ Falló'}")
                if user:
                    print(f"   - ID: {user.id}")
                    print(f"   - is_active: {user.is_active}")
            except Exception as e:
                print(f"❌ Error en authenticate(): {str(e)}")
                traceback.print_exc()
                messages.error(request, 'Error en autenticación.')
                return render(request, 'login.html')
            
            if user is not None:
                if user.is_active:
                    print("✅ Usuario activo")
                    registrar_log(username, 'login_exito', ip, 'Login exitoso')
                    
                    try:
                        cache.delete(intentos_key)
                    except:
                        pass
                    
                    login(request, user)
                    print(f"🔐 Usuario {user.username} logueado exitosamente")
                    messages.success(request, f'Bienvenido {user.username}')
                    return redirect('inventarios:dashboard')
                else:
                    print("⚠️ Usuario inactivo")
                    registrar_log(username, 'login_fallo', ip, 'Usuario inactivo')
                    messages.error(request, 'Usuario desactivado.')
            else:
                print("❌ Credenciales inválidas")
                intentos += 1
                try:
                    cache.set(intentos_key, intentos, 300)
                except:
                    pass
                
                registrar_log(username, 'login_fallo', ip, f'Intento {intentos}')
                
                if intentos >= 5:
                    try:
                        cache.set(f'bloqueado_{ip}', 15, 900)
                    except:
                        pass
                    messages.error(request, 'Demasiados intentos. Espere 15 minutos.')
                else:
                    messages.error(request, f'Usuario o contraseña incorrectos. Intentos: {5 - intentos}')
            
            return render(request, 'login.html')
        
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
        
        messages.error(request, 'Error interno del servidor.')
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