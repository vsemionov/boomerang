# from django.shortcuts import render

# Create your views here.

from collections import OrderedDict
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import viewsets, mixins, permissions, response, reverse

import apps
from .models import Notebook, Note, Task
import serializers, limits


class NestedObjectPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return str(request.user.username) == view.kwargs['user_username'] or \
               (request.user.is_staff and request.method in permissions.SAFE_METHODS)


class SyncedModelMixin(object):
    SINCE_PARAM = 'since'
    UNTIL_PARAM = 'until'

    def get_queryset(self):
        queryset = self._get_queryset()

        self.since = self.request.query_params.get(self.SINCE_PARAM)
        if self.since:
            queryset = queryset.filter(updated__gte=self.since)

        self.until = self.request.query_params.get(self.UNTIL_PARAM, now())
        if self.until:
            queryset = queryset.filter(updated__lt=self.until)

        return queryset

    def list(self, request, *args, **kwargs):
        orig_response = super(SyncedModelMixin, self).list(request, *args, **kwargs)
        orig_data = orig_response.data
        assert isinstance(orig_data, OrderedDict)
        data = OrderedDict(((self.SINCE_PARAM, self.since),
                            (self.UNTIL_PARAM, self.until)))
        data.update(orig_data)
        return response.Response(data)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    class Permissions(permissions.BasePermission):
        def has_permission(self, request, view):
            if view.action == 'retrieve':
                return str(request.user.username) == view.kwargs['username'] or \
                       (request.user.is_staff and request.method in permissions.SAFE_METHODS)
            else:
                # list
                return True

    lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, Permissions)

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
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def _get_queryset(self):
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
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def _get_queryset(self):
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
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def _get_queryset(self):
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
