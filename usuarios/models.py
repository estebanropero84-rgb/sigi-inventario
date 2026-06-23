# 📁 usuarios/models.py - CON VALIDACIONES DE SEGURIDAD
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone
import re


# ========== VALIDADORES PERSONALIZADOS (DENTRO DEL MODELO) ==========

def validar_username(value):
    """Valida que el nombre de usuario cumpla con los requisitos"""
    if not value:
        raise ValidationError("El nombre de usuario es obligatorio.")
    
    if len(value) < 3:
        raise ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
    
    if len(value) > 150:
        raise ValidationError("El nombre de usuario no puede tener más de 150 caracteres.")
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', value):
        raise ValidationError("El nombre de usuario solo puede contener letras, números, puntos, guiones y guiones bajos.")
    
    if value.isdigit():
        raise ValidationError("El nombre de usuario no puede ser solo números.")
    
    return value


def validar_email(value):
    """Valida que el email tenga formato correcto"""
    if not value:
        raise ValidationError("El correo electrónico es obligatorio.")
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValidationError("Ingresa un correo electrónico válido (ej: usuario@dominio.com).")
    
    return value


def validar_telefono(value):
    """Valida que el teléfono tenga formato correcto"""
    if value:
        if not re.match(r'^[0-9+\-() ]{7,15}$', value):
            raise ValidationError("Ingresa un número de teléfono válido (mínimo 7 dígitos).")
    return value


# ========== MODELO DE USUARIO ==========

class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('almacenista', 'Almacenista'),
        ('consultor', 'Consultor'),
    )
    
    # 🔥 VALIDACIONES DE SEGURIDAD EN LOS CAMPOS
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[validar_username],
        help_text="Mínimo 3 caracteres, solo letras, números, puntos, guiones y guiones bajos.",
        error_messages={
            'unique': "Este nombre de usuario ya está en uso.",
        }
    )
    
    email = models.EmailField(
        unique=True,
        validators=[validar_email],
        help_text="Ingresa un correo electrónico válido.",
        error_messages={
            'unique': "Este correo electrónico ya está registrado.",
        }
    )
    
    first_name = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(2, message="El nombre debe tener al menos 2 caracteres.")],
        help_text="Mínimo 2 caracteres."
    )
    
    last_name = models.CharField(
        max_length=150,
        validators=[MinLengthValidator(2, message="El apellido debe tener al menos 2 caracteres.")],
        help_text="Mínimo 2 caracteres."
    )
    
    rol = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='almacenista',
        help_text="Rol del usuario en el sistema."
    )
    
    telefono = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[validar_telefono],
        help_text="Formato: solo números, guiones y paréntesis (mínimo 7 dígitos)."
    )
    
    direccion = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
    
    # ========== PROPIEDADES PARA PERMISOS ==========
    
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
    
    @property
    def es_activo(self):
        return self.is_active
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    # ========== VALIDACIONES ADICIONALES ==========
    
    def clean(self):
        """Validaciones adicionales antes de guardar"""
        super().clean()
        
        # Validar que el nombre no esté vacío
        if self.first_name and len(self.first_name.strip()) < 2:
            raise ValidationError({'first_name': 'El nombre debe tener al menos 2 caracteres.'})
        
        if self.last_name and len(self.last_name.strip()) < 2:
            raise ValidationError({'last_name': 'El apellido debe tener al menos 2 caracteres.'})
        
        # Validar que el rol sea válido
        roles_validos = [rol[0] for rol in self.ROLES]
        if self.rol not in roles_validos:
            raise ValidationError({'rol': f'Rol inválido. Opciones: {", ".join(roles_validos)}'})
    
    def save(self, *args, **kwargs):
        """Guardar con validaciones automáticas"""
        # Si es superusuario, forzar rol admin
        if self.is_superuser and self.rol != 'admin':
            self.rol = 'admin'
        
        # Ejecutar validaciones
        self.full_clean()
        super().save(*args, **kwargs)
    
    # ========== MÉTODOS DE SEGURIDAD ==========
    
    def tiene_permiso(self, permiso):
        """Verifica si el usuario tiene un permiso específico"""
        permisos = {
            'editar_productos': self.puede_editar_productos,
            'ver_usuarios': self.puede_ver_usuarios,
            'editar_usuarios': self.puede_editar_usuarios,
            'editar_compras': self.puede_editar_compras,
        }
        return permisos.get(permiso, False)
    
    def get_permisos_lista(self):
        """Retorna lista de permisos del usuario"""
        permisos = []
        if self.puede_editar_productos:
            permisos.append('editar_productos')
        if self.puede_ver_usuarios:
            permisos.append('ver_usuarios')
        if self.puede_editar_usuarios:
            permisos.append('editar_usuarios')
        if self.puede_editar_compras:
            permisos.append('editar_compras')
        return permisos


# ========== LOGS DE SEGURIDAD ==========

class SeguridadLog(models.Model):
    """Registro de actividad sospechosa y eventos de seguridad"""
    
    ACCIONES = (
        ('login_fallo', 'Intento de login fallido'),
        ('login_exito', 'Login exitoso'),
        ('logout', 'Logout'),
        ('intento_bruteforce', 'Ataque de fuerza bruta detectado'),
        ('cambio_password', 'Cambio de contraseña'),
        ('acceso_denegado', 'Acceso denegado'),
        ('intento_admin', 'Intento de acceso a área admin sin permisos'),
        ('usuario_creado', 'Usuario creado'),
        ('usuario_eliminado', 'Usuario eliminado'),
        ('usuario_editado', 'Usuario editado'),
    )
    
    usuario = models.CharField(
        max_length=150, 
        null=True, 
        blank=True,
        help_text="Nombre de usuario (si está disponible)"
    )
    
    ip = models.GenericIPAddressField(
        help_text="Dirección IP del usuario"
    )
    
    accion = models.CharField(
        max_length=30, 
        choices=ACCIONES,
        help_text="Tipo de evento de seguridad"
    )
    
    detalles = models.TextField(
        blank=True, 
        null=True,
        help_text="Detalles adicionales del evento"
    )
    
    user_agent = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Navegador y sistema operativo del usuario"
    )
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora del evento"
    )
    
    class Meta:
        verbose_name = "Log de Seguridad"
        verbose_name_plural = "Logs de Seguridad"
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha']),
            models.Index(fields=['ip']),
            models.Index(fields=['accion']),
        ]
    
    def __str__(self):
        return f"{self.fecha.strftime('%d/%m/%Y %H:%M')} - {self.get_accion_display()} - {self.ip}"
    
    @classmethod
    def registrar(cls, usuario, ip, accion, detalles=None, user_agent=None):
        """Método para registrar eventos de seguridad fácilmente"""
        try:
            nombre_usuario = usuario.username if usuario else None
            return cls.objects.create(
                usuario=nombre_usuario,
                ip=ip,
                accion=accion,
                detalles=detalles,
                user_agent=user_agent
            )
        except Exception as e:
            # No fallar si no se puede registrar
            print(f"Error registrando log: {e}")
            return None
    
    @classmethod
    def registrar_intento_fallido(cls, usuario, ip, detalles=None, user_agent=None):
        """Registrar un intento de login fallido"""
        return cls.registrar(usuario, ip, 'login_fallo', detalles, user_agent)
    
    @classmethod
    def registrar_login_exitoso(cls, usuario, ip, user_agent=None):
        """Registrar un login exitoso"""
        return cls.registrar(usuario, ip, 'login_exito', user_agent=user_agent)
    
    @classmethod
    def registrar_bruteforce(cls, ip, detalles=None, user_agent=None):
        """Registrar un ataque de fuerza bruta"""
        return cls.registrar(None, ip, 'intento_bruteforce', detalles, user_agent)