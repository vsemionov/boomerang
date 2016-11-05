# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Value
from rest_framework import viewsets

from .models import Notebook, Note, Task
import serializers, permissions, limits, sync, search


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

    def get_deleted_parent_filter_kwargs(self, name):
        filter_kwargs = {}
        if self.deleted_parent is not None:
            filter_kwargs[name] = self.deleted_parent
        return filter_kwargs


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

    def lock_user(self):
        queryset = User.objects.filter(username=self.kwargs['user_username'])
        queryset = queryset.select_for_update()
        user = get_object_or_404(queryset)
        return user

    def get_hyperlinked_serializer_class(self):
        return serializers.get_hyperlinked_notebook_serializer_class(self.kwargs['user_username'])

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.lock_user()
        limits.check_limits(user, Notebook)
        serializer.save(user=user)


class BaseNoteBiewSet(SearchableSyncedModelViewSet):
    view_name = 'Note'
    lookup_field = 'ext_id'
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = permissions.nested_permissions
    full_text_vector = ('title', Value(' '), 'text')

    def get_view_name(self):
        name = self.view_name
        if self.suffix:
            name += ' ' + self.suffix
        return name


class NoteViewSet(BaseNoteBiewSet):
    def get_base_queryset(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('notebook__deleted')
        return Note.objects.filter(notebook__user_id=self.kwargs['user_username'],
                                   notebook_id=self.kwargs['notebook_ext_id'],
                                   **filter_kwargs)

    def get_notebook(self, lock=False):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('deleted')
        queryset = Notebook.objects.all()
        if lock:
            queryset = queryset.select_for_update()
        notebook = get_object_or_404(queryset,
                                     user_id=self.kwargs['user_username'],
                                     ext_id=self.kwargs['notebook_ext_id'],
                                     **filter_kwargs)
        return notebook

    def lock_notebook(self):
        return self.get_notebook(lock=True)

    def get_hyperlinked_serializer_class(self):
        return serializers.get_hyperlinked_note_serializer_class(self.kwargs['user_username'])

    def list(self, request, *args, **kwargs):
        self.get_notebook()
        return super(NoteViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        notebook = self.lock_notebook()
        limits.check_limits(notebook, Note)
        serializer.save(notebook=notebook)


class UserNoteViewSet(BaseNoteBiewSet):
    def get_base_queryset(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('notebook__deleted')
        return Note.objects.filter(notebook__user_id=self.kwargs['user_username'],
                                   **filter_kwargs)

    def get_user_notebooks(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('deleted')
        notebooks = Notebook.objects.filter(user_id=self.kwargs['user_username'],
                                            **filter_kwargs)
        return notebooks

    def lock_notebook(self, notebook):
        queryset = Notebook.objects.filter(id=notebook.id)
        queryset = queryset.select_for_update()
        notebook = get_object_or_404(queryset)
        return notebook

    def get_hyperlinked_serializer_class(self):
        notebooks = self.get_user_notebooks()
        return serializers.get_hyperlinked_note_serializer_class(self.kwargs['user_username'], notebooks)

    @transaction.atomic
    def perform_create(self, serializer):
        notebook = self.lock_notebook(serializer.validated_data['notebook'])
        limits.check_limits(notebook, Note)
        serializer.save()

    @transaction.atomic
    def perform_update(self, serializer):
        notebook = self.lock_notebook(serializer.validated_data['notebook'])
        limits.check_limits(notebook, Note)
        serializer.save()


class TaskViewSet(SearchableSyncedModelViewSet):
    lookup_field = 'ext_id'
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = permissions.nested_permissions
    full_text_vector = ('title', Value(' '), 'description')

    def get_base_queryset(self):
        return Task.objects.filter(user_id=self.kwargs['user_username'])

    def lock_user(self):
        queryset = User.objects.filter(username=self.kwargs['user_username'])
        queryset = queryset.select_for_update()
        user = get_object_or_404(queryset)
        return user

    def get_hyperlinked_serializer_class(self):
        return serializers.get_hyperlinked_task_serializer_class(self.kwargs['user_username'])

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.lock_user()
        limits.check_limits(user, Task)
        serializer.save(user=user)
