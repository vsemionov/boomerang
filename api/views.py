from django.contrib.auth.models import User
from rest_framework import viewsets, decorators
from rest_offline import limit
from rest_fuzzy import sort, search

from .models import Notebook, Note, Task
from .rest import serializers, links
from . import permissions


class UserViewSet(sort.SortedModelMixin,
                  search.SearchableModelMixin,
                  viewsets.ReadOnlyModelViewSet):
    lookup_field = 'username'
    lookup_value_regex = '[^/]+'
    queryset = User.objects.all()
    serializer_class = links.HyperlinkedUserSerializer
    permission_classes = permissions.user_permissions

    filter_backends = (search.SearchFilter, sort.OrderingFilter)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering_fields = ('username', 'date_joined', 'last_login', 'first_name', 'last_name', 'email')
    ordering = ('date_joined',)

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(id=self.request.user.id)

        return queryset


class NestedViewSet(sort.SortedModelMixin,
                    search.SearchableModelMixin,
                    limit.LimitedNestedSyncedModelMixin,
                    viewsets.ModelViewSet):
    lookup_field = 'ext_id'
    permission_classes = permissions.nested_permissions

    filter_backends = (search.SearchFilter, sort.OrderingFilter)
    ordering_fields = ('created', 'updated')
    ordering = ('created',)

    def get_hyperlinked_serializer_class(self, username):
        raise NotImplementedError()

    def get_serializer_class(self):
        if self.deleted_object:
            return self.serializer_class
        else:
            return self.get_hyperlinked_serializer_class(self.kwargs['user_username'])

    @decorators.list_route(suffix='Search')
    def search(self, request, *args, **kwargs):
        self.filter_backends = (search.RankedFuzzySearchFilter, sort.OrderingFilter)
        self.ordering_fields = ('rank',) + self.__class__.ordering_fields
        self.ordering = ('-rank',) + self.__class__.ordering

        return self.list(request, *args, **kwargs)


class UserChildViewSet(NestedViewSet):
    parent_model = User
    parent_path_model = User
    safe_parent_path = True
    object_filters = {'user_id': 'user_username'}
    parent_filters = {'username': 'user_username'}
    parent_key_filter = 'user_id'


class NotebookViewSet(UserChildViewSet):
    queryset = Notebook.objects.all()
    serializer_class = serializers.NotebookSerializer

    search_fields = ('name',)
    ordering_fields = ('created', 'updated', 'name')

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_notebook_serializer_class)


class TaskViewSet(UserChildViewSet):
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer

    search_fields = ('title', 'description')
    ordering_fields = ('created', 'updated', 'done', 'title')

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_task_serializer_class)


class NoteViewSet(NestedViewSet):
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer

    search_fields = ('title', 'text')
    ordering_fields = ('created', 'updated', 'title')

    parent_model = Notebook
    parent_path_model = Notebook
    safe_parent_path = False
    object_filters = {
        'notebook__user_id': 'user_username',
        'notebook_id': 'notebook_ext_id'
    }
    parent_filters = {
        'user_id': 'user_username',
        'ext_id': 'notebook_ext_id'
    }
    parent_key_filter = 'notebook_id'

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_note_serializer_class)


class UserNoteViewSet(NoteViewSet):
    view_name = 'Note'

    parent_model = Notebook
    parent_path_model = User
    safe_parent_path = True
    object_filters = {'notebook__user_id': 'user_username'}
    parent_filters = {'user_id': 'user_username'}
    parent_key_filter = 'notebook_id'

    def get_view_name(self):
        name = self.view_name

        if self.suffix:
            name += ' ' + self.suffix

        return name

    def get_hyperlinked_serializer_class(self, username):
        notebooks = self.get_parent_queryset(False, False)
        return links.create_hyperlinked_note_serializer_class(username, notebooks)
