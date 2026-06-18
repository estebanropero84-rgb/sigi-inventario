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
        
        # Verificar que el modelo existe
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
        # No fallamos la aplicación por error en logs
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
        # ============ INICIO DE LOGS DETALLADOS ============
        print(f"📌 URL: {request.path}")
        print(f"📌 Método HTTP: {request.method}")
        print(f"📌 Usuario autenticado: {request.user.is_authenticated}")
        print(f"📌 Session key: {request.session.session_key}")
        print(f"📌 Content-Type: {request.content_type}")
        print(f"📌 POST data: {request.POST}")
        # ===================================================
        
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
            # Continuamos si falla el caché
        
        if request.user.is_authenticated:
            print("✅ Usuario ya autenticado, redirigiendo a dashboard")
            return redirect('inventarios:dashboard')
        
        if request.method == 'POST':
            print("📥 Procesando POST de login")
            
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            print(f"👤 Username recibido: '{username}'")
            print(f"🔑 Password: {'***' if password else 'No recibida'}")
            print(f"📊 ¿Username vacío? {username is None or username == ''}")
            print(f"📊 ¿Password vacío? {password is None or password == ''}")
            
            if not username or not password:
                print("⚠️ Username o password vacíos")
                messages.error(request, 'Usuario y contraseña son requeridos')
                return render(request, 'login.html')
            
            # Contar intentos fallidos recientes
            try:
                intentos_key = f'intentos_{ip}'
                intentos = cache.get(intentos_key, 0)
                print(f"📊 Intentos fallidos previos: {intentos}")
            except Exception as e:
                print(f"⚠️ Error accediendo a caché: {e}")
                intentos = 0
            
            # Intentar autenticar
            print("🔍 Autenticando usuario con authenticate()...")
            print(f"   - username: {username}")
            print(f"   - password: {'***' if password else 'No'}")
            
            try:
                user = authenticate(request, username=username, password=password)
                print(f"👤 Resultado autenticación: {'✅ Éxito' if user else '❌ Falló'}")
                if user:
                    print(f"   - ID: {user.id}")
                    print(f"   - is_active: {user.is_active}")
                    print(f"   - is_superuser: {user.is_superuser}")
                    print(f"   - rol: {user.rol if hasattr(user, 'rol') else 'No tiene rol'}")
            except Exception as e:
                print(f"❌ Error en authenticate(): {str(e)}")
                print(f"   Stack:")
                traceback.print_exc()
                messages.error(request, f'Error en autenticación. Contacte al administrador.')
                return render(request, 'login.html')
            
            if user is not None:
                # Login exitoso
                print(f"✅ Usuario autenticado: {user.username}")
                
                if user.is_active:
                    print("✅ Usuario activo")
                    
                    # Registrar log de éxito
                    registrar_log(username, 'login_exito', ip, 'Login exitoso')
                    
                    # Limpiar intentos fallidos
                    try:
                        cache.delete(intentos_key)
                        print("🧹 Intentos fallidos limpiados del caché")
                    except Exception as e:
                        print(f"⚠️ Error limpiando caché: {e}")
                    
                    # Limpiar sesión antes de login
                    try:
                        request.session.flush()
                        print("🔄 Sesión limpiada")
                    except Exception as e:
                        print(f"⚠️ Error limpiando sesión: {e}")
                    
                    # Hacer login
                    try:
                        login(request, user)
                        print(f"🔐 Usuario {user.username} logueado exitosamente")
                        print(f"   - Session key después de login: {request.session.session_key}")
                    except Exception as e:
                        print(f"❌ Error en login(): {str(e)}")
                        print(f"   Stack:")
                        traceback.print_exc()
                        messages.error(request, f'Error iniciando sesión: {str(e)}')
                        return render(request, 'login.html')
                    
                    messages.success(request, f'Bienvenido {user.username}')
                    print("🎉 Login completado exitosamente, redirigiendo a dashboard")
                    print("=" * 70)
                    return redirect('inventarios:dashboard')
                else:
                    print("⚠️ Usuario inactivo (is_active=False)")
                    registrar_log(username, 'login_fallo', ip, 'Usuario inactivo')
                    messages.error(request, 'Usuario desactivado. Contacte al administrador.')
            else:
                # Login fallido
                print("❌ Credenciales inválidas - usuario no encontrado o contraseña incorrecta")
                
                intentos += 1
                try:
                    cache.set(intentos_key, intentos, 300)  # 5 minutos
                    print(f"📊 Intentos fallidos actualizados: {intentos} (guardado por 5 min)")
                except Exception as e:
                    print(f"⚠️ Error guardando intentos en caché: {e}")
                
                registrar_log(username, 'login_fallo', ip, f'Contraseña incorrecta (intento {intentos})')
                
                # Si hay 5 intentos fallidos, bloquear por 15 minutos
                if intentos >= 5:
                    try:
                        cache.set(f'bloqueado_{ip}', 15, 900)  # 15 minutos
                        print(f"⛔ IP {ip} bloqueada por 15 minutos (5 intentos fallidos)")
                    except Exception as e:
                        print(f"⚠️ Error bloqueando IP: {e}")
                    messages.error(request, 'Demasiados intentos fallidos. Intenta de nuevo en 15 minutos.')
                else:
                    messages.error(request, f'Usuario o contraseña incorrectos. Intentos restantes: {5 - intentos}')
            
            return render(request, 'login.html')
        
        # GET - Mostrar formulario
        print("📄 Mostrando formulario de login (GET)")
        print("=" * 70)
        return render(request, 'login.html')
        
    except Exception as e:
        print("=" * 70)
        print("❌❌❌ ERROR CRÍTICO EN LOGIN_VIEW ❌❌❌")
        print("=" * 70)
        print(f"Mensaje: {str(e)}")
        print(f"Tipo: {type(e).__name__}")
        print("Stack trace completo:")
        traceback.print_exc()
        print("=" * 70)
        
        # En producción, mostrar error genérico
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
    
    print("=" * 70)
    return redirect('login')