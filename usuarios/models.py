# 📁 usuarios/models.py - VERSIÓN CORRECTA (SIN IMPORTACIÓN CIRCULAR)
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('almacenista', 'Almacenista'),
        ('consultor', 'Consultor'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='almacenista')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'usuarios'
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
    
    @property
    def es_admin(self):
        return self.rol == 'admin'
    
    @property
    def es_almacenista(self):
        return self.rol == 'almacenista'
    
    @property
    def es_consultor(self):
        return self.rol == 'consultor'
    
    @property
    def puede_editar_productos(self):
        return self.rol in ['admin', 'almacenista']
    
    @property
    def puede_ver_usuarios(self):
        return self.rol == 'admin'
    
    @property
    def puede_editar_usuarios(self):
        return self.rol == 'admin'
    
    @property
    def puede_editar_compras(self):
        return self.rol == 'admin'
    
    def save(self, *args, **kwargs):
        if self.is_superuser and self.rol != 'admin':
            self.rol = 'admin'
        super().save(*args, **kwargs)


class SeguridadLog(models.Model):
    """Registro de actividad sospechosa y eventos de seguridad"""
    ACCIONES = (
        ('login_fallo', 'Intento de login fallido'),
        ('login_exito', 'Login exitoso'),
        ('logout', 'Logout'),
        ('intento_bruteforce', 'Ataque de fuerza bruta detectado'),
        ('cambio_password', 'Cambio de contraseña'),
        ('acceso_denegado', 'Acceso denegado'),
    )
    
    usuario = models.CharField(max_length=150, null=True, blank=True)
    ip = models.GenericIPAddressField()
    accion = models.CharField(max_length=30, choices=ACCIONES)
    detalles = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Log de Seguridad"
        verbose_name_plural = "Logs de Seguridad"
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.fecha} - {self.accion} - {self.ip}"