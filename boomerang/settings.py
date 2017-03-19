"""
Django settings for boomerang project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '26w+70vb7!sz!xm_j5tp-9dp5es^u^9dy0ykc0-lcu3v*b3@ke'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'boomerang.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'boomerang.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'ubuntu',
        'NAME': 'boomerang',
        'USER': 'boomerang',
        'PASSWORD': 'honda1',
        'CONN_MAX_AGE': 1800,
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'


# Email

ADMIN_NAME = 'Notes Admin'
SERVER_EMAIL = 'vsemionov.notes@gmail.com'
DEFAULT_FROM_EMAIL = '%s <%s>' % (ADMIN_NAME, SERVER_EMAIL)

EMAIL_HOST_USER = 'vsemionov.notes@gmail.com'
EMAIL_HOST_PASSWORD = 'noteslow'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

ADMINS = (
    (ADMIN_NAME, SERVER_EMAIL),
)
MANAGERS = ADMINS

# custom settings

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE = [
                     'debug_toolbar.middleware.DebugToolbarMiddleware',
                 ] + MIDDLEWARE
else:
    ALLOWED_HOSTS = ['vsemionov.pythonanywhere.com']
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]

INTERNAL_IPS = [
    '127.0.0.1',
]

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = 'index'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'api_throttle': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'cache_api_throttle',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 50*1000,
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.Pagination',
    'PAGE_SIZE': 25,
    'HTML_SELECT_CUTOFF': 50,
    'DEFAULT_THROTTLE_CLASSES': (
        'boomerang.throttle.UserRateThrottle',
        # 'boomerang.throttle.HostRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '120/min',
        'host': '120/min',
    },
}
if not DEBUG:
    REST_FRAMEWORK.update({
        'NUM_PROXIES': 1,
    })

ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_ADAPTER = 'boomerang.auth.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'boomerang.auth.SocialAccountAdapter'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 30


API_LIMITS = {
    'auth.User': {
        'api.Notebook': 8,
        'api.Task': 250,
    },
    'api.Notebook': {
        'api.Note': 125,
    },
}
API_MAX_PAGE_SIZE = 100
API_DELETED_EXPIRY_DAYS = 30