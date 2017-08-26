from django.core.exceptions import FieldDoesNotExist


def is_deletable(model):
    try:
        model._meta.get_field('deleted')
    except FieldDoesNotExist:
        return False

    return True
