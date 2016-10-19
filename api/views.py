# from django.shortcuts import render

# Create your views here.

from collections import OrderedDict
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, response, reverse

import apps
from .models import Notebook, Note, Task
import serializers


class NestedObjectPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return str(request.user.id) == view.kwargs['user_pk'] or \
               (request.user.is_staff and request.method in permissions.SAFE_METHODS)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    class Permissions(permissions.BasePermission):
        def has_permission(self, request, view):
            if view.action == 'retrieve':
                return str(request.user.id) == view.kwargs['pk'] or \
                       (request.user.is_staff and request.method in permissions.SAFE_METHODS)
            else:
                # list
                return True

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


class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = serializers.NotebookSerializer
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def get_queryset(self):
        return Notebook.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        return serializers.get_dynamic_notebook_serializer(self.kwargs)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def get_queryset(self):
        return Note.objects.filter(notebook__user_id=self.kwargs['user_pk'], notebook_id=self.kwargs['notebook_pk'])

    def get_notebook(self):
        notebook = get_object_or_404(Notebook.objects.all(),
                                     id=self.kwargs['notebook_pk'], user_id=self.kwargs['user_pk'])
        return notebook

    def list(self, request, *args, **kwargs):
        self.get_notebook()
        return super(NoteViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        notebook = self.get_notebook()
        serializer.save(notebook=notebook)

    def get_serializer_class(self):
        return serializers.get_dynamic_note_serializer(self.kwargs)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def get_queryset(self):
        return Task.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        return serializers.get_dynamic_task_serializer(self.kwargs)


class InfoViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    @staticmethod
    def _get_user_url(request):
        return request.user.id and reverse.reverse('user-detail', request=request, args=[request.user.id])

    def list(self, request, *args, **kwargs):
        app = OrderedDict((('name', apps.APP_NAME), ('version', apps.APP_VERSION)))
        user = OrderedDict((('id', request.user.id), ('url', self._get_user_url(request))))
        info = OrderedDict((('app', app), ('user', user)))
        return response.Response(info)
