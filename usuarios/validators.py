import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MinimumLengthValidator:
    """Valida que la contraseña tenga una longitud mínima"""
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("La contraseña debe tener al menos %(min_length)d caracteres."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return _(f"La contraseña debe tener al menos {self.min_length} caracteres.")


class NumberValidator:
    """Valida que la contraseña contenga al menos un número"""
    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                _("La contraseña debe contener al menos un número."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _("La contraseña debe contener al menos un número.")


class UppercaseValidator:
    """Valida que la contraseña contenga al menos una mayúscula"""
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos una letra mayúscula."),
                code='password_no_uppercase',
            )

    def get_help_text(self):
        return _("La contraseña debe contener al menos una letra mayúscula.")


class LowercaseValidator:
    """Valida que la contraseña contenga al menos una minúscula"""
    def validate(self, password, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("La contraseña debe contener al menos una letra minúscula."),
                code='password_no_lowercase',
            )

    def get_help_text(self):
        return _("La contraseña debe contener al menos una letra minúscula.")


class SpecialCharacterValidator:
    """Valida que la contraseña contenga al menos un carácter especial"""
    def __init__(self, special_chars=r'[!@#$%^&*(),.?":{}|<>]'):
        self.special_chars = special_chars

    def validate(self, password, user=None):
        if not re.search(self.special_chars, password):
            raise ValidationError(
                _("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>).")


class CommonPasswordValidator:
    """Valida que la contraseña no sea una de las más comunes"""
    COMMON_PASSWORDS = [
        'password', '123456', '12345678', '1234', 'qwerty',
        'abc123', 'monkey', 'letmein', 'dragon', '111111',
        'baseball', 'iloveyou', 'trustno1', '1234567', 'sunshine',
        'master', '123123', 'welcome', 'shadow', 'ashley',
        'football', 'jesus', 'michael', 'ninja', 'mustang',
        'password1', '123456789', '1234567890', 'admin', 'admin123'
    ]

    def validate(self, password, user=None):
        if password.lower() in self.COMMON_PASSWORDS:
            raise ValidationError(
                _("La contraseña es demasiado común. Por favor elige una más segura."),
                code='password_common',
            )

    def get_help_text(self):
        return _("No uses contraseñas comunes como 'password' o '123456'.")


class UsernameValidator:
    """Valida que el nombre de usuario cumpla con los requisitos"""
    def validate(self, username):
        if len(username) < 3:
            raise ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        
        if len(username) > 150:
            raise ValidationError("El nombre de usuario no puede tener más de 150 caracteres.")
        
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            raise ValidationError("El nombre de usuario solo puede contener letras, números, puntos, guiones y guiones bajos.")
        
        # Verificar que no sea solo números
        if username.isdigit():
            raise ValidationError("El nombre de usuario no puede ser solo números.")

    def get_help_text(self):
        return "Mínimo 3 caracteres, solo letras, números, puntos, guiones y guiones bajos."


class EmailValidator:
    """Valida que el email tenga formato correcto"""
    def validate(self, email):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingresa un correo electrónico válido.")

    def get_help_text(self):
        return "Ingresa un correo electrónico válido (ej: usuario@dominio.com)."