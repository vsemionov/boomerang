from django.conf import settings
from django.db import transaction
from django.db.models import Subquery
from rest_framework import exceptions, status

from .mixin import ViewSetMixin
from .models import TrackedModel


class LimitExceededError(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'limit exceeded'


# this mixin depends on NestedModelMixin
class LimitedModelMixin(ViewSetMixin):
    parent_key_filter = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_limits = False

    def get_limit(self, deleted):
        if settings.API_LIMITS is None:
            return None

        parent_limits = settings.API_LIMITS.get(self.parent_model._meta.label)
        if not parent_limits:
            return None

        child_limit = parent_limits.get(self.queryset.model._meta.label)
        if not child_limit:
            return None

        limit = child_limit[int(deleted)]
        if not limit:
            return None

        return limit

    def _check_active_limits(self, parent):
        limit = self.get_limit(False)
        if not limit:
            return

        object_type = self.queryset.model

        child_set_name = object_type._meta.model_name + '_set'
        child_set = getattr(parent, child_set_name)

        if issubclass(object_type, TrackedModel):
            child_set = child_set.filter(deleted=False)

        if child_set.count() >= limit:
            raise LimitExceededError('exceeded limit of %d %s per %s' %
                                     (limit, object_type._meta.verbose_name_plural, parent._meta.verbose_name))

    def _check_deleted_limits(self):
        limit = self.get_limit(True)
        if not limit:
            return

        field, kwarg = self.parent_key_filter
        filter_kwargs = {field: self.kwargs[kwarg]}
        filter_kwargs['deleted'] = True

        delete_ids = Subquery(self.queryset.filter(**filter_kwargs).order_by('-updated', '-id')[limit:].values('id'))
        self.queryset.filter(id__in=delete_ids).delete()

    def get_parent(self, lock):
        parent = super().get_parent(lock or self.check_limits)

        if self.check_limits:
            self._check_active_limits(parent)

        return parent

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)

        self._check_deleted_limits()

        return response

    @transaction.atomic(savepoint=False)
    def perform_create(self, serializer):
        self.check_limits = True
        return super().perform_create(serializer)
