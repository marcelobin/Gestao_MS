"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
#ALLOWED_HOSTS = ["*", "9db1-187-23-193-244.ngrok-free.app", "f7cd-187-23-193-244.ngrok-free.app"]
#CSRF_TRUSTED_ORIGINS = ['https://9db1-187-23-193-244.ngrok-free.app',
#                        'https://f7cd-187-23-193-244.ngrok-free.app',]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'clientes',
    'usuarios',
    'lojas',
    'financeiras',
    'propostas',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_plotly_dash',  # Mantenha esta
    'channels',    
    'dashboard',
    'rest_framework',
    'corsheaders',
    'dpd_static_support',
    'widget_tweaks',
    'configuracao',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_plotly_dash.middleware.BaseMiddleware',
    'django_plotly_dash.middleware.ExternalRedirectionMiddleware',
    'core.middleware.SessionTimeoutMiddleware'
    ]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]


PLOTLY_DASH = {
    "ws_route": None,
    "http_route": "dash_http",
    "http_use_redirect": True,
    "insert_into_iframe" : False,
}

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_plotly_dash.finders.DashAssetFinder',
    'django_plotly_dash.finders.DashComponentFinder',
    'django_plotly_dash.finders.DashAppDirectoryFinder',
]

PLOTLY_COMPONENTS = [
    'dash_core_components',
    'dash_html_components',
    'dash_renderer',
    'dpd_static_support',
    'plotly',
    'dash_table',

]


ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

WSGI_APPLICATION = 'core.wsgi.application'

ASGI_APPLICATION = "core.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Porta padrão do Redis
        },
    },
}



# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Campo_Grande'

USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'

# Diretório onde o Django procura por arquivos estáticos durante o desenvolvimento
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Diretório de desenvolvimento
]

# Diretório onde os arquivos estáticos serão coletados para produção
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Diretório para arquivos coletados


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Formato para exibição e entrada de datas
DATE_FORMAT = 'd/m/Y'  # Exibe datas como dd/mm/aaaa
DATE_INPUT_FORMATS = ['%d/%m/%Y']  # Aceita dd/mm/aaaa no input

X_FRAME_OPTIONS = 'SAMEORIGIN'

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/index/'  # Página para onde o usuário será redirecionado após o login

# Sessão do usuário - Tempo de expiração e segurança
SESSION_COOKIE_AGE = 30 * 60  # 30 minutos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Força logout ao fechar o navegador
SESSION_SAVE_EVERY_REQUEST = True  # Salva a sessão a cada requisição para resetar o timer
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Armazena sessões no banco de dados

# WebSockets com Redis - Expira conexões após 30 minutos
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
            "expiry": 1800,  # Expira conexões do Redis após 30 minutos
        },
    },
}
