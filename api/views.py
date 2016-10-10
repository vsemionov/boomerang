# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from rest_framework import viewsets, mixins, permissions, exceptions

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

    def _validate_notebook(self, serializer):
        if serializer.validated_data['notebook'].user_id != self.request.user.id:
            raise exceptions.PermissionDenied("can not add note to another user's notebook")

    def perform_create(self, serializer):
        self._validate_notebook(serializer)
        serializer.save()

    def perform_update(self, serializer):
        self._validate_notebook(serializer)
        serializer.save()


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
