from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    # Si ya está autenticado, redirige al dashboard
    if request.user.is_authenticated:
        return redirect('inventarios:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}')
            return redirect('inventarios:dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')