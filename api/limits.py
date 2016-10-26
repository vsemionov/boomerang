from django.contrib.auth.models import User
from rest_framework import exceptions
from .models import Notebook, Note, Task


LIMITS = {
    User: {
        Notebook: 8,
        Task: 128,
    },
    Notebook: {
        Note: 128,
    },
}


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
        raise exceptions.PermissionDenied('can not create more than %d %s per %s' % \
                                          (limit, child_type._meta.verbose_name_plural, parent._meta.verbose_name))
