import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# Seguridad / Config básica
# =========================
# IMPORTANTE:
# - En producción NO hardcodees la clave. Usa variable de entorno DJANGO_SECRET_KEY.
# - Para desarrollo local puedes dejar el fallback (pero no lo subas a un repo público).
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-cambia-esto-por-una-clave-larga-y-aleatoria"
)

DEBUG = True
ALLOWED_HOSTS = ["*"]

# =========================
# Apps
# =========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Mis apps
    'usuarios',
    'Productos',
    'compras',
    'movimientos',
    'inventarios',
    'login',
]

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Sigi_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Sigi_admin.wsgi.application'

# =========================
# Base de datos PostgreSQL
# =========================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sigi_db',
        'USER': 'postgres',
        'PASSWORD': '1234',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# =========================
# Password validators
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================
# i18n / TZ
# =========================
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# =========================
# Static
# =========================
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================
# Auth redirects
# =========================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Configuración de correo electrónico (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_correo@gmail.com'  # 🔥 Cambia por tu correo
EMAIL_HOST_PASSWORD = 'tu_contraseña_de_aplicacion'  # 🔥 Usa contraseña de aplicación
DEFAULT_FROM_EMAIL = 'SIGI <tu_correo@gmail.com>'

# URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
# ========== SEGURIDAD - CONFIGURACIÓN COMPLETA ==========

# 1. HASHING DE CONTRASEÑAS (bcrypt - el más seguro)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# 2. HEADERS DE SEGURIDAD
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# 3. COOKIES SEGURAS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 1800  # 30 minutos de inactividad
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_SAMESITE = 'Strict'

# 4. HTTPS (solo en producción, para desarrollo usa False)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 5. LÍMITES DE CARGA
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000
DATA_UPLOAD_MAX_NUMBER_FILES = 10
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# 6. SEGURIDAD DE SESIÓN
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# 7. RATE LIMITING
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'Sigi_admin.middleware.SecurityHeadersMiddleware',  # 🔥 Agregar
    'Sigi_admin.middleware.IpLoggerMiddleware',        # 🔥 Agregar
    
]
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}