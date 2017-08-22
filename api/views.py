# from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import viewsets, decorators

from .models import Notebook, Note, Task
from .rest import serializers, links
from .mixins import sync, search, sort
from . import permissions, limits


class SortedSearchableSyncedModelViewSet(sort.SortedModelMixin,
                                         search.SearchableModelMixin,
                                         sync.SyncedModelMixin,
                                         viewsets.ModelViewSet):
    no_content_actions = {'destroy'}

    filter_backends = (search.SearchFilter, sort.OrderingFilter)

    ordering = sort.consistent_sort(sort.SortedModelMixin.DEFAULT_SORT)

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

    @decorators.list_route(suffix='Search')
    def search(self, request, *args, **kwargs):
        self.perform_search = True
        self.full_text_search = True
        self.disabled_mixins = {sort.SortedModelMixin, sync.SyncedModelMixin}
        self.filter_backends = ()
        return self.list(request, *args, **kwargs)


class UserChildViewSet(SortedSearchableSyncedModelViewSet):
    def get_base_queryset(self):
        return self.queryset.filter(user_id=self.kwargs['user_username'])

    def lock_user(self):
        queryset = User.objects.filter(username=self.kwargs['user_username'])
        queryset = queryset.select_for_update()
        user = get_object_or_404(queryset)
        return user

    def hyperlinked_serializer_class_func(self, username):
        raise NotImplementedError()

    def get_hyperlinked_serializer_class(self):
        return self.hyperlinked_serializer_class_func(self.kwargs['user_username'])

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.lock_user()
        limits.check_limits(user, self.queryset.model)
        serializer.save(user=user)


class BaseNoteViewSet(SortedSearchableSyncedModelViewSet):
    view_name = 'Note'
    lookup_field = 'ext_id'
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer
    permission_classes = permissions.nested_permissions

    search_fields = ('title', 'text')
    ordering_fields = ('created', 'updated', 'title')

    def get_view_name(self):
        name = self.view_name
        if self.suffix:
            name += ' ' + self.suffix
        return name


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'username'
    lookup_value_regex = '[^/]+'
    queryset = User.objects.all()
    serializer_class = links.HyperlinkedUserSerializer
    permission_classes = permissions.user_permissions

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = User.objects.filter(id=self.request.user.id)

        return queryset


class NotebookViewSet(UserChildViewSet):
    lookup_field = 'ext_id'
    queryset = Notebook.objects.all()
    serializer_class = serializers.NotebookSerializer
    permission_classes = permissions.nested_permissions

    hyperlinked_serializer_class_func = staticmethod(links.create_hyperlinked_notebook_serializer_class)

    search_fields = ('name',)
    ordering_fields = ('created', 'updated', 'name')


class TaskViewSet(UserChildViewSet):
    lookup_field = 'ext_id'
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = permissions.nested_permissions

    hyperlinked_serializer_class_func = staticmethod(links.create_hyperlinked_task_serializer_class)

    search_fields = ('title', 'description')
    ordering_fields = ('created', 'updated', 'done', 'title')


class NoteViewSet(BaseNoteViewSet):
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
        return links.create_hyperlinked_note_serializer_class(self.kwargs['user_username'])

    def list(self, request, *args, **kwargs):
        self.get_notebook()
        return super(NoteViewSet, self).list(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        notebook = self.lock_notebook()
        limits.check_limits(notebook, Note)
        serializer.save(notebook=notebook)


class UserNoteViewSet(BaseNoteViewSet):
    @staticmethod
    def lock_notebook(notebook):
        queryset = Notebook.objects.filter(id=notebook.id)
        queryset = queryset.select_for_update()
        notebook = get_object_or_404(queryset)
        return notebook

    def get_base_queryset(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('notebook__deleted')
        return Note.objects.filter(notebook__user_id=self.kwargs['user_username'],
                                   **filter_kwargs)

    def get_user_notebooks(self):
        filter_kwargs = self.get_deleted_parent_filter_kwargs('deleted')
        notebooks = Notebook.objects.filter(user_id=self.kwargs['user_username'],
                                            **filter_kwargs)
        return notebooks

    def get_hyperlinked_serializer_class(self):
        notebooks = self.get_user_notebooks()
        return links.create_hyperlinked_note_serializer_class(self.kwargs['user_username'], notebooks)

    @transaction.atomic
    def perform_create(self, serializer):
        notebook = self.lock_notebook(serializer.validated_data['notebook'])
        limits.check_limits(notebook, Note)
        serializer.save()

    def perform_update(self, serializer):
        notebook = self.lock_notebook(serializer.validated_data['notebook'])
        limits.check_limits(notebook, Note)
        super(UserNoteViewSet, self).perform_update(serializer)
