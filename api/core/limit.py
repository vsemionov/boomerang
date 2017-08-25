from django.conf import settings
from django.db import transaction
from django.db.models import Subquery
from rest_framework import exceptions, status

from .mixin import ViewSetMixin
from .. import util


class LimitExceededError(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'limit exceeded'


# this mixin depends on NestedModelMixin
class LimitedModelMixin(ViewSetMixin):
    parent_key_filter = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_limits = False

    @staticmethod
    def _get_limit(parent, child_type, deleted):
        parent_limits = settings.API_LIMITS.get(parent._meta.label)
        if not parent_limits:
            return None

        child_limit = parent_limits.get(child_type._meta.label)
        if not child_limit:
            return None

        limit = child_limit[int(deleted)]
        if not limit:
            return None

        return limit

    def _check_active_limits(self, parent):
        child_type = self.queryset.model

        limit = self._get_limit(parent, child_type, False)
        if not limit:
            return

        child_set_name = child_type._meta.model_name + '_set'
        child_set = getattr(parent, child_set_name)

        if util.is_deletable(child_type):
            child_set = child_set.filter(deleted=False)

        if child_set.count() >= limit:
            raise LimitExceededError('exceeded limit of %d %s per %s' %
                                     (limit, child_type._meta.verbose_name_plural, parent._meta.verbose_name))

    def _check_deleted_limits(self):
        child_type = self.queryset.model

        limit = self._get_limit(self.parent_model, child_type, True)
        if not limit:
            return

        field, kwarg = self.parent_key_filter
        filter_kwargs = {field: self.kwargs[kwarg]}
        filter_kwargs['deleted'] = True

        queryset = child_type.objects.filter(**filter_kwargs)

        delete_ids = Subquery(queryset.order_by('-updated', '-id')[limit:].values('id'))
        queryset.filter(id__in=delete_ids).delete()

    def get_parent_queryset(self):
        queryset = super().get_parent_queryset()

        if self.check_limits:
            queryset = queryset.select_for_update()

        return queryset

    def get_parent(self):
        parent = super().get_parent()

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
