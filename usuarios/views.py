from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q

from .models import Usuario
from .decorators import admin_required
from .models import SeguridadLog

@login_required
@admin_required
def logs_seguridad(request):
    """Ver logs de seguridad (solo admin)"""
    logs = SeguridadLog.objects.all().order_by('-fecha')[:100]
    
    # Estadísticas
    intentos_fallidos = SeguridadLog.objects.filter(accion='login_fallo').count()
    accesos_sospechosos = SeguridadLog.objects.filter(accion='intento_bruteforce').count()
    
    return render(request, 'usuarios/logs_seguridad.html', {
        'logs': logs,
        'intentos_fallidos': intentos_fallidos,
        'accesos_sospechosos': accesos_sospechosos,
    })


@login_required
@admin_required
def listar_usuarios(request):
    """Lista de usuarios (solo admin)"""
    usuarios_qs = Usuario.objects.all().order_by('-date_joined')

    busqueda = (request.GET.get('buscar') or '').strip()
    if busqueda:
        usuarios_qs = usuarios_qs.filter(
            Q(username__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda)
        )

    paginator = Paginator(usuarios_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'usuarios/lista.html', {
        'usuarios': page_obj,
        'busqueda': busqueda,
    })


@login_required
@admin_required
def crear_usuario(request):
    """Crear nuevo usuario (solo admin)"""
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        password = request.POST.get('password') or ''
        password2 = request.POST.get('password2') or ''
        rol = (request.POST.get('rol') or 'consultor').strip()

        # Validaciones
        if not username:
            messages.error(request, 'El usuario (username) es obligatorio.')
            return render(request, 'usuarios/crear.html', {'data': request.POST})

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'usuarios/crear.html', {'data': request.POST})

        if not password:
            messages.error(request, 'La contraseña es obligatoria.')
            return render(request, 'usuarios/crear.html', {'data': request.POST})

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'usuarios/crear.html', {'data': request.POST})

        # Crear (con manejo de error visible)
        try:
            with transaction.atomic():
                Usuario.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    rol=rol,
                    is_active=True
                )
        except Exception as e:
            messages.error(request, f'Error creando usuario: {e}')
            return render(request, 'usuarios/crear.html', {'data': request.POST})

        messages.success(request, f'Usuario {username} creado exitosamente.')
        return redirect('usuarios:listar')

    return render(request, 'usuarios/crear.html')


@login_required
@admin_required
def editar_usuario(request, pk):
    """Editar usuario existente (solo admin)"""
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        rol = (request.POST.get('rol') or usuario.rol).strip()
        is_active = request.POST.get('is_active') == 'on'
        nueva_password = request.POST.get('password') or ''

        if not username:
            messages.error(request, 'El usuario (username) es obligatorio.')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})

        if Usuario.objects.filter(username=username).exclude(id=usuario.id).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})

        try:
            with transaction.atomic():
                usuario.username = username
                usuario.email = email
                usuario.first_name = first_name
                usuario.last_name = last_name
                usuario.rol = rol
                usuario.is_active = is_active

                if nueva_password:
                    usuario.set_password(nueva_password)

                usuario.save()
        except Exception as e:
            messages.error(request, f'Error actualizando usuario: {e}')
            return render(request, 'usuarios/editar.html', {'usuario': usuario})

        messages.success(request, f'Usuario {username} actualizado exitosamente.')
        return redirect('usuarios:listar')

    return render(request, 'usuarios/editar.html', {'usuario': usuario})


@login_required
@admin_required
def eliminar_usuario(request, pk):
    """Eliminar usuario (solo admin)"""
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
        return redirect('usuarios:listar')

    if request.method == 'POST':
        username = usuario.username
        try:
            usuario.delete()
        except Exception as e:
            messages.error(request, f'Error eliminando usuario: {e}')
            return redirect('usuarios:listar')

        messages.success(request, f'Usuario {username} eliminado.')
        return redirect('usuarios:listar')

    return render(request, 'usuarios/eliminar.html', {'usuario': usuario})


@login_required
def perfil(request):
    """Perfil del usuario actual con estadísticas y actividad reciente"""
    usuario = request.user
    
    # Obtener logs del usuario actual (últimos 10)
    logs_usuario = SeguridadLog.objects.filter(usuario=usuario).order_by('-fecha')[:10]
    
    # Estadísticas del usuario
    intentos_fallidos = SeguridadLog.objects.filter(
        usuario=usuario, 
        accion='login_fallo'
    ).count()
    
    accesos_sospechosos = SeguridadLog.objects.filter(
        usuario=usuario,
        accion='intento_bruteforce'
    ).count()
    
    # Total de logs del usuario
    total_logs = SeguridadLog.objects.filter(usuario=usuario).count()
    
    context = {
        'usuario': usuario,
        'logs_usuario': logs_usuario,
        'intentos_fallidos': intentos_fallidos,
        'accesos_sospechosos': accesos_sospechosos,
        'total_logs': total_logs,
    }
    
    return render(request, 'usuarios/perfil.html', context)