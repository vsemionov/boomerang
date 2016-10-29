from collections import OrderedDict
from django.db import transaction
from django.utils import timezone, dateparse
from rest_framework import decorators, exceptions, status, response


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'conflict'


class SyncedModelMixin(object):
    AT_PARAM = 'at'
    SINCE_PARAM = 'since'
    UNTIL_PARAM = 'until'

    supported_write_conditions = (AT_PARAM, UNTIL_PARAM)
    exclusive_write_conditions = (AT_PARAM, UNTIL_PARAM)

    def __init__(self, *args, **kwargs):
        self.at = None
        self.since = None
        self.until = None
        self.deleted_parent = False
        super(SyncedModelMixin, self).__init__(*args, **kwargs)

    def get_timestamp(self, name, default=None):
        timestamp_reprs = self.request.query_params.getlist(name)
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
        queryset = self.get_base_queryset()

        if self.action in ('list', 'deleted'):
            if self.since:
                queryset = queryset.filter(updated__gte=self.since)
            if self.until:
                queryset = queryset.filter(updated__lt=self.until)

        if self.action in ('update', 'partial_update', 'destroy'):
            queryset = queryset.select_for_update()

        if self.action == 'deleted':
            queryset = queryset.filter(deleted=True)
        else:
            queryset = queryset.filter(deleted=False)

        return queryset

    def list(self, request, *args, **kwargs):
        self.since = self.get_timestamp(self.SINCE_PARAM)
        self.until = self.get_timestamp(self.UNTIL_PARAM, timezone.now())

        base_response = super(SyncedModelMixin, self).list(request, *args, **kwargs)
        base_data = base_response.data
        assert isinstance(base_data, OrderedDict)

        data = OrderedDict(((self.SINCE_PARAM, self.since),
                            (self.UNTIL_PARAM, self.until)))
        data.update(base_data)

        return response.Response(data)

    def init_write_conditions(self):
        self.at = self.get_timestamp(self.AT_PARAM)
        self.until = self.get_timestamp(self.UNTIL_PARAM)

        exclusive_conditions = [param for param in self.request.query_params
                                if param in self.exclusive_write_conditions]
        if len(exclusive_conditions) > 1:
            raise exceptions.ValidationError("unsupported combination: " + ', '.join(exclusive_conditions))

        unsupported_conditions = [param for param in self.request.query_params
                                  if param not in self.supported_write_conditions]
        if unsupported_conditions:
            unsupported_condition = unsupported_conditions[0]
            raise exceptions.ValidationError({unsupported_condition: 'unsupported condition'})

    def check_write_conditions(self, instance):
        if self.at and instance.updated != self.at:
                raise ConflictError()
        if self.until and instance.updated >= self.until:
                raise ConflictError()

    def create(self, request, *args, **kwargs):
        self.deleted_parent = None
        return super(SyncedModelMixin, self).create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.deleted_parent = None
        self.init_write_conditions()
        return super(SyncedModelMixin, self).update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        self.deleted_parent = None
        self.init_write_conditions()
        return super(SyncedModelMixin, self).destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.check_write_conditions(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self.check_write_conditions(instance)
        instance.deleted = True
        instance.save()

    @decorators.list_route()
    def deleted(self, request, *args, **kwargs):
        self.deleted_parent = None
        return self.list(request, *args, **kwargs)
