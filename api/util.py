from django.conf import settings


def is_pgsql():
    return settings.DATABASES['default']['ENGINE'].startswith('django.db.backends.postgresql')

def get_view_description(cld, html=False):
    return ''
