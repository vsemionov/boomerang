# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Value
from rest_framework import viewsets

from .models import Notebook, Note, Task
import serializers, permissions, limits, sync, search


WILDCARD_ID = 'all'


class SearchableSyncedModelViewSet(search.SearchableModelMixin,
                                   sync.SyncedModelMixin,
                                   viewsets.ModelViewSet):
    def get_hyperlinked_serializer_class(self):
        raise NotImplementedError()

    def get_serializer_class(self):
        if self.deleted_object:
            return self.serializer_class
        else:
            return self.get_hyperlinked_serializer_class()


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


class NotebookViewSet(SearchableSyncedModelViewSet):
    lookup_field = 'ext_id'
    queryset = Notebook.objects.all()
    serializer_class = serializers.NotebookSerializer
    permission_classes = permissions.nested_permissions
    full_text_vector = ('name', Value(' '))

    def get_base_queryset(self):
        return Notebook.objects.filter(user_id=self.kwargs['user_username'])

    def get_hyperlinked_serializer_class(self):
        return serializers.get_hyperlinked_notebook_serializer_class(self.kwargs['user_username'])

    def perform_create(self, serializer):
        user = self.request.user
        limits.check_limits(user, Notebook)
        serializer.save(user=user)


class NoteViewSet(SearchableSyncedModelViewSet):
    lookup_field = 'ext_id'
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = permissions.nested_permissions
    full_text_vector = ('title', Value(' '), 'text')

    def get_deleted_parent_filter_kwargs(self, name):
        filter_kwargs = {}
        if self.deleted_parent is not None:
            filter_kwargs[name] = self.deleted_parent
        return filter_kwargs

    def get_base_queryset(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('notebook__deleted')
        if self.kwargs['notebook_ext_id'] != WILDCARD_ID:
            filter_kwargs['notebook_id'] = self.kwargs['notebook_ext_id']
        return Note.objects.filter(notebook__user_id=self.kwargs['user_username'],
                                   **filter_kwargs)

    def get_notebook(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('deleted')
        notebook = get_object_or_404(Notebook.objects.all(),
                                     user_id=self.kwargs['user_username'],
                                     ext_id=self.kwargs['notebook_ext_id'],
                                     **filter_kwargs)
        return notebook

    def get_hyperlinked_serializer_class(self):
        return serializers.get_hyperlinked_note_serializer_class(self.kwargs['user_username'])

    def list(self, request, *args, **kwargs):
        if self.kwargs['notebook_ext_id'] != WILDCARD_ID:
            self.get_notebook()
        return super(NoteViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        notebook = self.get_notebook()
        limits.check_limits(notebook, Note)
        serializer.save(notebook=notebook)


class TaskViewSet(SearchableSyncedModelViewSet):
    lookup_field = 'ext_id'
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = permissions.nested_permissions
    full_text_vector = ('title', Value(' '), 'description')

    def get_base_queryset(self):
        return Task.objects.filter(user_id=self.kwargs['user_username'])

    def get_hyperlinked_serializer_class(self):
        return serializers.get_hyperlinked_task_serializer_class(self.kwargs['user_username'])

    def perform_create(self, serializer):
        user = self.request.user
        limits.check_limits(user, Task)
        serializer.save(user=user)
