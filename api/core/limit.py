from django.conf import settings
from django.db import transaction
from django.db.models import Subquery
from django.shortcuts import get_object_or_404
from rest_framework import exceptions, status

from .mixin import ViewSetMixin
from .models import TrackedModel


class LimitExceededError(exceptions.APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'limit exceeded'


class LimitedModelMixin(ViewSetMixin):
    parent_key_filter = None

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

    def _evict_deleted_peers(self, instance):
        limit = self.get_limit(True)
        if not limit:
            return

        filter_kwargs = {}
        filter_kwargs[self.parent_key_filter] = getattr(instance, self.parent_key_filter)
        filter_kwargs['deleted'] = True

        delete_ids = Subquery(self.queryset.filter(**filter_kwargs).order_by('-updated', '-id')[limit:].values('id'))

        delete_objs = self.queryset.filter(id__in=delete_ids)
        delete_objs.delete()

    def locked_parent(self, parent):
        queryset = self.parent_model.objects.filter(pk=parent.pk)

        queryset = queryset.select_for_update()

        locked = get_object_or_404(queryset)

        return locked

    @transaction.atomic(savepoint=False)
    def perform_create(self, serializer):
        parent_name = self.get_parent_name()

        save_kwargs = {}

        if self.is_aggregate():
            parent = self.locked_parent(serializer.validated_data[parent_name])
        else:
            parent = self.get_parent(False, True)

            save_kwargs = {parent_name: parent}

        self._check_active_limits(parent)

        serializer.save(**save_kwargs)

    @transaction.atomic(savepoint=False)
    def perform_update(self, serializer):
        if self.is_aggregate():
            parent = self.locked_parent(serializer.validated_data[self.get_parent_name()])

            self._check_active_limits(parent)

        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)

        self._evict_deleted_peers(instance)
