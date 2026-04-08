from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Usuario
from .decorators import admin_required

@login_required
@admin_required
def listar_usuarios(request):
    """Lista de usuarios (solo admin)"""
    usuarios = Usuario.objects.all().order_by('-date_joined')
    
    # Búsqueda
    busqueda = request.GET.get('buscar', '')
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(email__icontains=busqueda) |
            Q(first_name__icontains=busqueda)
        )
    
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'usuarios/lista.html', {'usuarios': page_obj})

@login_required
@admin_required
def crear_usuario(request):
    """Crear nuevo usuario (solo admin)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        rol = request.POST.get('rol')
        
        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return redirect('usuarios:crear')
        
        usuario = Usuario.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            rol=rol,
            is_active=True
        )
        
        messages.success(request, f'Usuario {username} creado exitosamente')
        return redirect('usuarios:listar')
    
    return render(request, 'usuarios/crear.html')

@login_required
@admin_required
def editar_usuario(request, pk):
    """Editar usuario existente (solo admin)"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        rol = request.POST.get('rol')
        is_active = request.POST.get('is_active') == 'on'
        
        # Verificar si el username ya existe (excepto el actual)
        if Usuario.objects.filter(username=username).exclude(id=usuario.id).exists():
            messages.error(request, 'El nombre de usuario ya existe')
            return redirect('usuarios:editar', pk=usuario.id)
        
        usuario.username = username
        usuario.email = email
        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.rol = rol
        usuario.is_active = is_active
        
        # Si se proporciona nueva contraseña, actualizarla
        nueva_password = request.POST.get('password')
        if nueva_password:
            usuario.set_password(nueva_password)
        
        usuario.save()
        
        messages.success(request, f'Usuario {username} actualizado exitosamente')
        return redirect('usuarios:listar')
    
    return render(request, 'usuarios/editar.html', {'usuario': usuario})

@login_required
@admin_required
def eliminar_usuario(request, pk):
    """Eliminar usuario (solo admin)"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir eliminar el propio usuario
    if usuario.id == request.user.id:
        messages.error(request, 'No puedes eliminar tu propio usuario')
        return redirect('usuarios:listar')
    
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario {username} eliminado')
        return redirect('usuarios:listar')
    
    return render(request, 'usuarios/eliminar.html', {'usuario': usuario})

@login_required
def perfil(request):
    """Perfil del usuario actual"""
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})