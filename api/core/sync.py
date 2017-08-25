import datetime
from collections import OrderedDict

from django.conf import settings
from django.db import transaction
from django.utils import timezone, dateparse
from rest_framework import decorators, exceptions, status

from .mixin import ViewSetMixin


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'conflict'


class SyncedModelMixin(ViewSetMixin):
    AT_PARAM = 'at'
    SINCE_PARAM = 'since'
    UNTIL_PARAM = 'until'

    supported_write_conditions = (AT_PARAM, UNTIL_PARAM)
    exclusive_write_conditions = (AT_PARAM, UNTIL_PARAM)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.at = None
        self.since = None
        self.until = None

        self.atomic = False

        self.deleted_object = False

    @staticmethod
    def get_timestamp(request, name, default=None):
        timestamp_reprs = request.query_params.getlist(name)
        if len(timestamp_reprs) > 1:
            raise exceptions.ValidationError({name: 'multiple timestamp values'})

        if timestamp_reprs:
            timestamp_repr = timestamp_reprs[0]
            timestamp = dateparse.parse_datetime(timestamp_repr)
            if timestamp is None:
                raise exceptions.ValidationError({name: 'invalid timestamp format'})
            if timestamp.tzinfo is None:
                raise exceptions.ValidationError({name: 'timestamp without timezone'})
        else:
            timestamp = default

        return timestamp

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.since:
            queryset = queryset.filter(updated__gte=self.since)
        if self.until:
            queryset = queryset.filter(updated__lt=self.until)

        if self.atomic:
            queryset = queryset.select_for_update()

        if self.deleted_object is not None:
            queryset = queryset.filter(deleted=self.deleted_object)

        return queryset

    def list(self, request, *args, **kwargs):
        self.since = self.get_timestamp(request, self.SINCE_PARAM)
        self.until = self.get_timestamp(request, self.UNTIL_PARAM, timezone.now())

        data = OrderedDict(((self.SINCE_PARAM, self.since),
                            (self.UNTIL_PARAM, self.until)))

        return self.decorated_base_list(SyncedModelMixin, data, request, *args, **kwargs)

    @decorators.list_route(suffix='Deleted List')
    def deleted(self, request, *args, **kwargs):
        self.deleted_object = True

        response = self.list(request, *args, **kwargs)

        if self.since is None or self.since < (timezone.now() - datetime.timedelta(settings.API_DELETED_EXPIRY_DAYS)):
            response.status_code = status.HTTP_206_PARTIAL_CONTENT

        return response


class ReadWriteSyncedModelMixin(SyncedModelMixin):

    def _init_write_conditions(self, request):
        self.at = self.get_timestamp(request, self.AT_PARAM)
        self.until = self.get_timestamp(request, self.UNTIL_PARAM)

        exclusive_conditions = [param for param in request.query_params
                                if param in self.exclusive_write_conditions]
        if len(exclusive_conditions) > 1:
            raise exceptions.ValidationError("unsupported combination: " + ', '.join(exclusive_conditions))

        unsupported_conditions = [param for param in request.query_params
                                  if param not in self.supported_write_conditions]
        if unsupported_conditions:
            unsupported_condition = unsupported_conditions[0]
            raise exceptions.ValidationError({unsupported_condition: 'unsupported condition'})

    def _check_write_conditions(self, instance):
        if self.at and instance.updated != self.at:
                raise ConflictError()
        if self.until and instance.updated >= self.until:
                raise ConflictError()

    @transaction.atomic(savepoint=False)
    def update(self, request, *args, **kwargs):
        self.atomic = True
        self._init_write_conditions(request)
        return super().update(request, *args, **kwargs)

    @transaction.atomic(savepoint=False)
    def destroy(self, request, *args, **kwargs):
        self.atomic = True
        self._init_write_conditions(request)
        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        self._check_write_conditions(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._check_write_conditions(instance)
        instance.deleted = True
        instance.save()
