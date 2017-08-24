from django.conf import settings
from django.db import transaction
from rest_framework import exceptions, status

from .mixin import ViewSetMixin
from .. import util


class LimitExceededError(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'limit exceeded'


# this mixin depends on NestedModelMixin
class LimitedModelMixin(ViewSetMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_limits = False

    def check_limits(self, parent):
        child_type = self.queryset.model

        parent_limits = settings.API_LIMITS.get(parent._meta.label)
        if not parent_limits:
            return

        limit = parent_limits.get(child_type._meta.label)
        if not limit:
            return

        child_set_name = child_type._meta.default_related_name
        child_set = getattr(parent, child_set_name)

        if util.is_deletable(child_type):
            child_set = child_set.filter(deleted=False)

        if child_set.count() >= limit:
            raise LimitExceededError('exceeded limit of %d %s per %s' %
                                     (limit, child_type._meta.verbose_name_plural, parent._meta.verbose_name))

    def get_parent_queryset(self):
        queryset = super().get_parent_queryset()

        if self.check_limits:
            queryset = queryset.select_for_update()

        return queryset

    def get_parent(self):
        parent = super().get_parent()

        if self.check_limits:
            self.check_limits(parent)

        return parent

    @transaction.atomic
    def perform_create(self, serializer):
        self.check_limits = True
        return super().perform_create(serializer)
