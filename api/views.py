# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, permissions, response, reverse

import apps
from .models import Notebook, Note, Task
from .serializers import UserSerializer, NotebookSerializer, NoteSerializer, TaskSerializer


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
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, Permissions)

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        else:
            return User.objects.filter(id=self.request.user.id)


class NotebookViewSet(viewsets.ModelViewSet):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def get_queryset(self):
        return Notebook.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def get_queryset(self):
        return Note.objects.filter(notebook__user_id=self.kwargs['user_pk'], notebook_id=self.kwargs['notebook_pk'])

    def perform_create(self, serializer):
        serializer.save(notebook_id=self.kwargs['notebook_pk'])


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated, NestedObjectPermissions)

    def get_queryset(self):
        return Task.objects.filter(user_id=self.kwargs['user_pk'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InfoViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    @staticmethod
    def _get_user_url(request):
        return request.user.id and reverse.reverse('user-detail', request=request, args=[request.user.id])

    def list(self, request, *args, **kwargs):
        app = dict(name=apps.APP_NAME, version=apps.APP_VERSION)
        user = dict(id=request.user.id, url=self._get_user_url(request))
        info = dict(app=app, user=user)
        return response.Response(info)
