# from django.shortcuts import render

# Create your views here.

from collections import OrderedDict
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone, dateparse
from django.db import transaction
from rest_framework import viewsets, mixins, permissions, exceptions, status, response, reverse

import apps
from .models import Notebook, Note, Task
import serializers, permissions, limits


class ModifiedError(exceptions.APIException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = 'precondition failed'


class SyncedModelMixin(object):
    AT_PARAM = 'at'
    SINCE_PARAM = 'since'
    UNTIL_PARAM = 'until'

    def __init__(self, *args, **kwargs):
        self.at = None
        self.since = None
        self.until = None
        super(SyncedModelMixin, self).__init__(*args, **kwargs)

    def get_timestamp(self, name, default=None):
        timestamp_repr = self.request.query_params.get(name)

        if timestamp_repr:
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

        if self.action == 'list':
            if self.since:
                queryset = queryset.filter(updated__gte=self.since)
            if self.until:
                queryset = queryset.filter(updated__lt=self.until)

        if self.action in ('update', 'partial_update', 'destroy'):
            queryset = queryset.select_for_update()

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

        if self.at and self.until:
            raise exceptions.ValidationError("can not combine 'at' and 'until'")

    def check_write_conditions(self, instance):
        if self.at and instance.updated != self.at:
                raise ModifiedError('modified')
        if self.until and instance.updated >= self.until:
                raise ModifiedError('modified')

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        self.init_write_conditions()
        return super(SyncedModelMixin, self).update(request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        self.init_write_conditions()
        return super(SyncedModelMixin, self).destroy(request, *args, **kwargs)

    def perform_update(self, serializer):
        self.check_write_conditions(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self.check_write_conditions(instance)
        instance.delete()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = permissions.user_permissions

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        else:
            return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        return serializers.get_dynamic_user_serializer()


class NotebookViewSet(SyncedModelMixin,
                      viewsets.ModelViewSet):
    lookup_field = 'ext_id'
    queryset = Notebook.objects.all()
    serializer_class = serializers.NotebookSerializer
    permission_classes = permissions.nested_permissions

    def get_base_queryset(self):
        return Notebook.objects.filter(user_id=self.kwargs['user_username'])

    def get_serializer_class(self):
        return serializers.get_dynamic_notebook_serializer(self.kwargs)

    def perform_create(self, serializer):
        user = user = self.request.user
        limits.check_limits(user, Notebook)
        serializer.save(user=user)


class NoteViewSet(SyncedModelMixin,
                  viewsets.ModelViewSet):
    lookup_field = 'ext_id'
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = permissions.nested_permissions

    def get_base_queryset(self):
        return Note.objects.filter(notebook__user_id=self.kwargs['user_username'],
                                   notebook_id=self.kwargs['notebook_ext_id'])

    def get_notebook(self):
        notebook = get_object_or_404(Notebook.objects.all(),
                                     ext_id=self.kwargs['notebook_ext_id'], user_id=self.kwargs['user_username'])
        return notebook

    def get_serializer_class(self):
        return serializers.get_dynamic_note_serializer(self.kwargs)

    def list(self, request, *args, **kwargs):
        self.get_notebook()
        return super(NoteViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        notebook = self.get_notebook()
        limits.check_limits(notebook, Note)
        serializer.save(notebook=notebook)


class TaskViewSet(SyncedModelMixin,
                  viewsets.ModelViewSet):
    lookup_field = 'ext_id'
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = permissions.nested_permissions

    def get_base_queryset(self):
        return Task.objects.filter(user_id=self.kwargs['user_username'])

    def get_serializer_class(self):
        return serializers.get_dynamic_task_serializer(self.kwargs)

    def perform_create(self, serializer):
        user = user = self.request.user
        limits.check_limits(user, Task)
        serializer.save(user=user)


class InfoViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    view_name = 'Info'

    @staticmethod
    def _get_user_url(request):
        return request.user.id and reverse.reverse('user-detail', request=request, args=[request.user.username])

    def get_view_name(self):
        return self.view_name

    def list(self, request, *args, **kwargs):
        app = OrderedDict((('name', apps.APP_NAME),
                           ('version', apps.APP_VERSION)))
        user = OrderedDict((('username', request.user.username),
                            ('url', self._get_user_url(request))))
        info = OrderedDict((('app', app),
                            ('user', user)))
        return response.Response(info)
