"""
Django settings for project_config project.

Generated by 'django-admin startproject' using Django 3.2.22.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/

Deployment checklist
See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
"""


from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# ENVIRONMENT
# =============================================================================

# Read .env
# See https://docs.djangoproject.com/en/3.2/ref/settings/#std:settings-ENV
env = environ.Env()
environ.Env.read_env(BASE_DIR.parent / ".env")

# Secret key
# SECURITY WARNING: keep the secret key used in production secret!
# See https://docs.djangoproject.com/en/3.2/ref/settings/#secret-key
SECRET_KEY = env("SECRET_KEY")

# Debug
# SECURITY WARNING: don't run with debug turned on in production!
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/#debug
DEBUG = env("DEBUG")

# Allowed hosts
# See https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Database
# See https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': env.db("DATABASE_URL")
}

# Email
# https://docs.djangoproject.com/en/3.2/ref/settings/#email-backend
EMAIL_BACKEND = env("EMAIL_BACKEND")

# Mode (DEV or PROD)
MODE = env("MODE")


# =============================================================================
# DJANGO
# =============================================================================

# Application definition
# See https://docs.djangoproject.com/en/3.2/ref/settings/#installed-apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "authenticate",
    "core",

]

# Middleware
# See https://docs.djangoproject.com/en/3.2/topics/http/middleware/
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Root URLs
# See https://docs.djangoproject.com/en/3.2/ref/settings/#root-urls
ROOT_URLCONF = 'project_config.urls'

# Templates
# See https://docs.djangoproject.com/en/3.2/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# WSGI Application
# See https://docs.djangoproject.com/en/3.2/ref/settings/#wsgi-application
WSGI_APPLICATION = 'project_config.wsgi.application'

# Password validation
# See https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators
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
# See https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# See https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'

# Default primary key field type
# See https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTH_USER_MODEL = 'authenticate.CustomUser'


if MODE == "DEV":

    # Static files (CSS, JavaScript, Images)
    # See https://docs.djangoproject.com/en/3.2/howto/static-files/
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'static'

    # Media files
    # See https://docs.djangoproject.com/en/3.2/howto/static-files/#media-files
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    