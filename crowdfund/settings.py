# crowdfund/settings.py

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# УБИРАЕМ ненужные приложения (мы не используем стандартную аутентификацию Django)
INSTALLED_APPS = [
    # 'django.contrib.admin',        # ← УБРАНО
    'django.contrib.auth', 
    'django.contrib.contenttypes', 
    'django.contrib.sessions',       # ← ОСТАВЛЕНО для сессий
    'django.contrib.messages',       # ← ОСТАВЛЕНО для сообщений
    'django.contrib.staticfiles',
    'rest_framework',
    'projects',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # ← ПУСТОЙ СПИСОК! (шаблоны ищутся автоматически в app/templates/)
        'APP_DIRS': True,  # ← ОБЯЗАТЕЛЬНО True
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                # УБРАНО: 'django.contrib.auth.context_processors.auth' (не нужен без auth)
            ],
        },
    },
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ← Нужен для сессий
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware', \
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'crowdfund.urls'
WSGI_APPLICATION = 'crowdfund.wsgi.application'

# 🔥 КРИТИЧЕСКИ ВАЖНО: Настраиваем ФАЙЛОВЫЕ сессии вместо базы данных
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_FILE_PATH = os.path.join(BASE_DIR, 'sessions')  # Папка для хранения сессий
SESSION_COOKIE_AGE = 1209600  # 2 недели

# Полностью отключаем ORM Django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.dummy',
    }
}

# Статика и медиа
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Создаём директории для медиа при запуске
if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

AVATARS_DIR = os.path.join(MEDIA_ROOT, 'avatars')
if not os.path.exists(AVATARS_DIR):
    os.makedirs(AVATARS_DIR)

# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # ← Разрешаем всем по умолчанию
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# Создаём папку для сессий при запуске
if not os.path.exists(SESSION_FILE_PATH):
    os.makedirs(SESSION_FILE_PATH)