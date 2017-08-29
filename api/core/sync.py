import time
import datetime
from collections import OrderedDict

from django.conf import settings
from django.db import transaction
from django.utils import timezone, dateparse
from rest_framework import exceptions, status, decorators

from .delete import DeletableModelMixin


class ConflictError(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'conflict'


class SyncedModelMixin(DeletableModelMixin):
    AT_PARAM = 'at'
    SINCE_PARAM = 'since'
    UNTIL_PARAM = 'until'

    supported_write_conditions = (AT_PARAM,)
    exclusive_write_conditions = (AT_PARAM,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.at = None

        self.since = None
        self.until = None

        self.isolated = False

    @staticmethod
    def get_timestamp(request, name, default=None):
        timestamp_reprs = request.query_params.getlist(name)

        if len(timestamp_reprs) > 1:
            raise exceptions.ValidationError({name: 'multiple timestamp values'})

        if timestamp_reprs:
            timestamp = dateparse.parse_datetime(timestamp_reprs[0])

            if timestamp is None:
                raise exceptions.ValidationError({name: 'invalid timestamp format'})
            if timestamp.tzinfo is None:
                raise exceptions.ValidationError({name: 'timestamp without timezone'})
        else:
            timestamp = default

        return timestamp

    def _is_expired(self):
        if settings.API_DELETED_EXPIRY_DAYS is None:
            return False

        if self.since is None:
            return True

        return self.since < (timezone.now() - datetime.timedelta(settings.API_DELETED_EXPIRY_DAYS))

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.since:
            queryset = queryset.filter(updated__gte=self.since)
        if self.until:
            queryset = queryset.filter(updated__lt=self.until)

        if self.isolated:
            queryset = queryset.select_for_update()

        return queryset

    def list(self, request, *args, **kwargs):
        self.since = self.get_timestamp(request, self.SINCE_PARAM)
        self.until = self.get_timestamp(request, self.UNTIL_PARAM, timezone.now())

        data = OrderedDict(((self.SINCE_PARAM, self.since),
                            (self.UNTIL_PARAM, self.until)))

        return self.decorated_base_list(SyncedModelMixin, data, request, *args, **kwargs)

    @decorators.list_route(suffix='Archive')
    def deleted(self, request, *args, **kwargs):
        response = super().deleted(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            if self._is_expired():
                response.status_code = status.HTTP_206_PARTIAL_CONTENT

        return response

    @staticmethod
    def _ensure_updated_past(instance):
        while True:
            now = timezone.now()

            if instance.updated < now:
                break

            if instance.updated > now:
                raise ValueError('updated timestamp is in the future')

            time.sleep(0.001)

    def _init_write_conditions(self, request):
        unsupported_conditions = [param for param in request.query_params
                                  if param not in self.supported_write_conditions]
        if unsupported_conditions:
            raise exceptions.ValidationError({cond: 'unsupported condition' for cond in unsupported_conditions})

        exclusive_conditions = [param for param in request.query_params
                                if param in self.exclusive_write_conditions]
        if len(exclusive_conditions) > 1:
            raise exceptions.ValidationError("unsupported combination: " + ', '.join(exclusive_conditions))

        self.at = self.get_timestamp(request, self.AT_PARAM)

    def _check_write_conditions(self, instance):
        if self.at and instance.updated != self.at:
                raise ConflictError()
        if self.until and instance.updated >= self.until:
                raise ConflictError()

    @transaction.atomic(savepoint=False)
    def update(self, request, *args, **kwargs):
        self.isolated = True

        self._init_write_conditions(request)

        return super().update(request, *args, **kwargs)

    @transaction.atomic(savepoint=False)
    def destroy(self, request, *args, **kwargs):
        self.isolated = True

        self._init_write_conditions(request)

        return super().destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        self._check_write_conditions(serializer.instance)

        self._ensure_updated_past(serializer.instance)

        serializer.save()

    def perform_destroy(self, instance):
        self._check_write_conditions(instance)

        self._ensure_updated_past(instance)

        super().perform_destroy(instance)
