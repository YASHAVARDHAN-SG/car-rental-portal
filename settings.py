
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEBUG = os.environ.get("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-development-only-key")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

if not DEBUG:
    if SECRET_KEY == "local-development-only-key":
        raise RuntimeError("DJANGO_SECRET_KEY must be configured when DEBUG is disabled.")
    if not ALLOWED_HOSTS:
        raise RuntimeError("Set DJANGO_ALLOWED_HOSTS when DEBUG is disabled.")

INSTALLED_APPS = [
 'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
 'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles',
 'car','bicycle',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ.get('DJANGO_DB_PATH', BASE_DIR / 'db.sqlite3'),
    }
}
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
LOGIN_URL = '/login/'
