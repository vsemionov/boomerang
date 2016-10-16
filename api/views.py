# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, mixins, permissions, response, reverse

import apps
from .models import Notebook, Note, Task
from .serializers import UserSerializer, NotebookSerializer, NoteSerializer, TaskSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    class Permissions(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return request.user.id == obj.id or request.user.is_staff

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, Permissions)

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset
        else:
            # list
            if self.request.user.is_staff:
                return self.queryset
            else:
                return self.queryset.filter(id=self.request.user.id)


class NotebookViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    class Permissions(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return request.user.id == obj.user_id or \
                   (request.user.is_staff and request.method in permissions.SAFE_METHODS)

    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer
    permission_classes = (permissions.IsAuthenticated, Permissions)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    class Permissions(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return request.user.id == obj.notebook.user_id or \
                   (request.user.is_staff and request.method in permissions.SAFE_METHODS)

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated, Permissions)

    def get_serializer_class(self):
        user_id = self.request.user.id
        notebook_queryset = Notebook.objects.filter(user_id=user_id)

        class DynamicNoteSerializer(NoteSerializer):
            notebook = serializers.HyperlinkedRelatedField(view_name='notebook-detail', queryset=notebook_queryset)
        return DynamicNoteSerializer


class TaskViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    class Permissions(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return request.user.id == obj.user_id or \
                   (request.user.is_staff and request.method in permissions.SAFE_METHODS)

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated, Permissions)

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
