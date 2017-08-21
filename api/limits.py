from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from rest_framework import exceptions, status


class LimitExceededError(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'limit exceeded'


def check_limits(parent, child_type):
    parent_limits = settings.API_LIMITS.get(parent._meta.label)
    if not parent_limits:
        return

    limit = parent_limits.get(child_type._meta.label)
    if limit is None:
        return

    child_set_name = child_type._meta.verbose_name + '_set'
    child_set = getattr(parent, child_set_name)

    try:
        child_type._meta.get_field('deleted')
    except FieldDoesNotExist:
        effective_child_set = child_set
    else:
        effective_child_set = child_set.filter(deleted=False)

    if effective_child_set.count() >= limit:
        raise LimitExceededError('exceeded limit of %d %s per %s' %
                                 (limit, child_type._meta.verbose_name_plural, parent._meta.verbose_name))
