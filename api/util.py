from django.conf import settings


def is_pgsql():
    return settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql'
