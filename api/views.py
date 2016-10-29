# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .models import Notebook, Note, Task
import serializers, permissions, limits, sync


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


class NotebookViewSet(sync.SyncedModelMixin,
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


class NoteViewSet(sync.SyncedModelMixin,
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


class TaskViewSet(sync.SyncedModelMixin,
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
