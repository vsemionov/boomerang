from django.contrib.auth.models import User
from rest_framework import exceptions, status
from .models import Notebook, Note, Task


LIMITS = {
    User: {
        Notebook: 8,
        Task: 125,
    },
    Notebook: {
        Note: 250,
    },
}


class LimitExceededError(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'limit exceeded'


def check_limits(parent, child_type):
    parent_limits = LIMITS.get(parent.__class__)
    if not parent_limits:
        return

    limit = parent_limits.get(child_type)
    if limit is None:
        return

    child_set_name = child_type._meta.verbose_name + '_set'
    child_set = getattr(parent, child_set_name)
    if child_set.count() >= limit:
        raise LimitExceededError('exceeded limit of %d %s per %s' % \
                                 (limit, child_type._meta.verbose_name_plural, parent._meta.verbose_name))
