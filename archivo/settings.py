"""
Django settings for archivo project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
from .settings_secret import *
import os
from django.utils.translation import gettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.241.128.56', 'archivogam.haverford.edu']


# Application definition

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'gam_app',
    'ckeditor',
    'storages',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'mapwidgets',
    'acceso',
    #    'django-datatables-view',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "gam_app/locale"),
    os.path.join(BASE_DIR, "acceso/locale"),
]

ROOT_URLCONF = 'archivo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(
                BASE_DIR, 'gam_app/templates', './templates', 'acceso/templates'
            )
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ]
        },
    }
]

WSGI_APPLICATION = 'archivo.wsgi.application'

SITE_ID = 2
# from https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'
    },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/


LANGUAGE_CODE = 'es'
LANGUAGES = [('es', _('Español')), ('de', _('Deutsch')), ('en', _('English'))]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/html/static/'
MEDIA_ROOT = "media/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'gam_app/static'),
    os.path.join(BASE_DIR, 'acceso/static'),
]

ACCOUNT_ACTIVATION_DAYS = 30
REGISTRATION_OPEN = True

CKEDITOR_CONFIGS = {
    'default': {
        'allowedContent': True,
        'height': 600,
        'width': 600,
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Copy', 'Styles'],
            ['language', 'Source'],
        ],
    }
}

MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocationName", [14.642213, -90.516653]),
        (
            "GooglePlaceAutocompleteOptions",
            {'componentRestrictions': {'country': 'uk'}},
        ),
        ("markerFitZoom", 12),
    ),
    "GOOGLE_MAP_API_KEY": "AIzaSyDWqgDyEf7Vk4pURXc4mLQEeIFsLqRD-KI",
}
GOOGLE_MAP_API_KEY = 'AIzaSyDWqgDyEf7Vk4pURXc4mLQEeIFsLqRD-KI'
