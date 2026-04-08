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
    
    def save(self, *args, **kwargs):
        # Si es superusuario, asignar rol admin automáticamente
        if self.is_superuser and self.rol != 'admin':
            self.rol = 'admin'
        super().save(*args, **kwargs)