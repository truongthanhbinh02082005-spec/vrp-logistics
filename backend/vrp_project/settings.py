from pathlib import Path
from datetime import timedelta
from decouple import config
try:
    import dj_database_url
except ImportError:
    dj_database_url = None
import mimetypes

mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("text/css", ".css", True)

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']

# CSRF & CORS Security (Fix 403 Forbidden)
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.koyeb.app',
    'https://*.hf.space',
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_extensions',
    'authentication',
    'warehouses',
    'vehicles',
    'orders',
    'transport',
    'reports',
    'transactions',
    'benchmark',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'vrp_project.urls'

# Cho phép Hugging Face nhúng vào iframe
X_FRAME_OPTIONS = 'ALLOWALL'

# Static & Media serving
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# React Frontend Build integration
FRONTEND_BUILD_DIR = BASE_DIR / 'frontend_build'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [FRONTEND_BUILD_DIR],
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

STATICFILES_DIRS = [
    str(FRONTEND_BUILD_DIR / 'static'),
]

# WhiteNoise Optimization
WHITENOISE_ROOT = str(FRONTEND_BUILD_DIR)
WHITENOISE_INDEX_PAGE_SELF_REDIRECT = True
WHITENOISE_MANIFEST_STRICT = False

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Database logic
if dj_database_url and config('DATABASE_URL', default=None):
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600)
    }
elif config('DB_NAME', default=None):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'authentication.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
