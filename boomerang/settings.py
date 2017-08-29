"""
Django settings for boomerang project.

Generated by 'django-admin startproject' using Django 1.10.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
import urllib
import datetime

import dj_database_url


PROJECT_NAME = 'vsemionov.boomerang.api'
PROJECT_VERSION = '0.8.0'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', '26w+70vb7!sz!xm_j5tp-9dp5es^u^9dy0ykc0-lcu3v*b3@ke')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
DEBUG = "DYNO" not in os.environ

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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    'bootstrapform',
    'corsheaders',
    'api',
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


NUM_PROCS = int(os.getenv('NUM_WORKERS', 4))
REDIS_MAX_CONNS = int(os.getenv('REDIS_MAX_CONNS', 20))


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'NAME': 'boomerang',
        'USER': 'boomerang',
        'PASSWORD': 'honda1',
        'CONN_MAX_AGE': 0,
    }
}

db_from_env = dj_database_url.config(conn_max_age=1800)
DATABASES['default'].update(db_from_env)


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

ADMIN_NAME = 'Boomerang Notes'
SERVER_EMAIL = 'boomerang.notes@gmail.com'
DEFAULT_FROM_EMAIL = '%s <%s>' % (ADMIN_NAME, SERVER_EMAIL)

EMAIL_HOST_USER = 'boomerang.notes@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD', 'noteslow')

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
    ALLOWED_HOSTS = [os.environ['API_HOST']]
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

LOGIN_REDIRECT_URL = 'api-root'
ACCOUNT_LOGOUT_REDIRECT_URL = 'api-root'

redis_url = urllib.parse.urlparse(os.getenv('REDIS_URL', 'redis://:honda1@localhost:6379/0'))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'api_throttle': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://{0}@{1}:{2}/{3}'.format(
            ':' + redis_url.password if redis_url.password is not None else '',
            redis_url.hostname,
            int(redis_url.port or 6379),
            int(redis_url.path.strip('/')) if redis_url.path else 0),
        'TIMEOUT': 300,
        'KEY_PREFIX': 'boomerang',
        'OPTIONS': {
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_CLASS': 'redis.connection.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': REDIS_MAX_CONNS // NUM_PROCS,
                'timeout': 5,
            },
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'api.pagination.Pagination',
    'PAGE_SIZE': 25,
    'HTML_SELECT_CUTOFF': 50,
    'DEFAULT_THROTTLE_CLASSES': (
        'api.throttle.UserRateThrottle',
        # 'api.throttle.HostRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'user': '120/min',
        'host': '120/min',
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}
if not DEBUG:
    REST_FRAMEWORK.update({
        'NUM_PROXIES': 2,
    })

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=1800),
}

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
        'api.Notebook': (8, 8),
        'api.Task': (250, 250),
    },
    'api.Notebook': {
        'api.Note': (125, 125),
    },
}
API_MAX_PAGE_SIZE = 100
API_DELETED_EXPIRY_DAYS = 30


CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ORIGIN_WHITELIST = []

ALLOW_ORIGIN = os.getenv('ALLOW_ORIGIN')
if ALLOW_ORIGIN:
    CORS_ORIGIN_WHITELIST = [ALLOW_ORIGIN]
if DEBUG:
    CORS_ORIGIN_WHITELIST.extend(['localhost:3000', '127.0.0.1:3000'])


ALLOWED_REDIRECT_URLS = set()
FRONTEND_LOGIN_REDIRECT_URL = os.getenv('FRONTEND_LOGIN_REDIRECT_URL')
if FRONTEND_LOGIN_REDIRECT_URL:
    ALLOWED_REDIRECT_URLS = {FRONTEND_LOGIN_REDIRECT_URL}
if DEBUG:
    ALLOWED_REDIRECT_URLS.update({
        'http://localhost:3000/login/success',
        'http://127.0.0.1:3000/login/success',
    })


sentry_dsn = os.getenv('SENTRY_DSN')
if sentry_dsn:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

RAVEN_CONFIG = {
    'dsn': sentry_dsn,
    'release': PROJECT_VERSION,
}


# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console'],
#             'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
#         },
#     },
# }
