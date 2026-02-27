from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ── Segredos via variáveis de ambiente ───────────────────────────
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-inseguro-mude-em-producao')
DEBUG      = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ── Aplicações ────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'axes',   # proteção contra força bruta
    'core',
]

# ── Middleware (whitenoise logo após security, axes por último) ────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # serve estáticos em produção
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_permissions',
                'core.context_processors.system_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Banco de dados ────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':     os.getenv('DB_NAME', 'django_app'),
        'USER':     os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST':     os.getenv('DB_HOST', 'localhost'),
        'PORT':     os.getenv('DB_PORT', '5432'),
    }
}

# ── Autenticação backend (axes substitui o padrão) ────────────────
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ── Validação de senha ────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Proteção contra força bruta (django-axes) ─────────────────────
AXES_FAILURE_LIMIT      = 3
AXES_COOLOFF_TIME       = 1
AXES_LOCKOUT_TEMPLATE   = 'lockout.html'
AXES_RESET_ON_SUCCESS   = True
AXES_ENABLE_ADMIN       = True
AXES_LOCKOUT_PARAMETERS  = ['ip_address']
AXES_LOCK_OUT_AT_FAILURE = True
AXES_ONLY_ADMIN_SITE    = False
AXES_WHITELIST_CALLABLE = 'core.config_utils.axes_whitelist'

# ── Segurança de sessão e cookies ─────────────────────────────────
SESSION_COOKIE_HTTPONLY  = True
SESSION_COOKIE_SAMESITE  = 'Lax'
SESSION_COOKIE_AGE       = 28800
CSRF_COOKIE_HTTPONLY     = False
CSRF_COOKIE_SAMESITE     = 'Lax'

# CSRF — origens confiáveis (inclui domínio do Coolify via env)
_trusted = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _trusted.split(',') if o.strip()]

# Segurança HTTPS (ativada automaticamente quando não DEBUG)
if not DEBUG:
    SESSION_COOKIE_SECURE  = True
    CSRF_COOKIE_SECURE     = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ── Cabeçalhos de segurança ───────────────────────────────────────
X_FRAME_OPTIONS             = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER   = True

# ── Internacionalização ───────────────────────────────────────────
LANGUAGE_CODE = 'pt-br'
TIME_ZONE     = 'America/Sao_Paulo'
USE_I18N      = True
USE_TZ        = True

# ── Estáticos (whitenoise serve em produção) ──────────────────────
STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Auth redirects ────────────────────────────────────────────────
LOGIN_URL           = '/login/'
LOGIN_REDIRECT_URL  = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
