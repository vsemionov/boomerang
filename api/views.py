from django.contrib.auth.models import User
from rest_framework import viewsets, decorators

from .models import Notebook, Note, Task
from .rest import serializers, links
from .mixins import sync, nest, limit, search, sort
from . import permissions


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


class NestedViewSet(sort.SortedModelMixin,
                    search.SearchableModelMixin,
                    limit.LimitedModelMixin,
                    nest.NestedModelMixin,
                    sync.SyncedModelMixin,
                    viewsets.ModelViewSet):
    permission_classes = permissions.nested_permissions

    filter_backends = (search.SearchFilter, sort.OrderingFilter)

    ordering = sort.consistent_sort(sort.SortedModelMixin.DEFAULT_SORT)  # TODO: check usage

    def get_hyperlinked_serializer_class(self, username):
        raise NotImplementedError()

    def get_serializer_class(self):
        if self.deleted_object:
            return self.serializer_class
        else:
            return self.get_hyperlinked_serializer_class(self.kwargs['user_username'])

    @decorators.list_route(suffix='Search')
    def search(self, request, *args, **kwargs):
        self.explicit_search = True
        self.full_text_search = True
        self.disabled_mixins = {sort.SortedModelMixin, sync.SyncedModelMixin}
        self.filter_backends = ()
        return self.list(request, *args, **kwargs)


class UserChildViewSet(NestedViewSet):
    parent_model = User
    safe_parent = True

    object_filters = {'user_id': 'user_username'}
    parent_filters = {'username': 'user_username'}


class NotebookViewSet(UserChildViewSet):
    lookup_field = 'ext_id'
    queryset = Notebook.objects.all()
    serializer_class = serializers.NotebookSerializer

    search_fields = ('name',)
    ordering_fields = ('created', 'updated', 'name')

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_notebook_serializer_class)


class TaskViewSet(UserChildViewSet):
    lookup_field = 'ext_id'
    queryset = Task.objects.all()
    serializer_class = serializers.TaskSerializer

    search_fields = ('title', 'description')
    ordering_fields = ('created', 'updated', 'done', 'title')

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_task_serializer_class)


class BaseNoteViewSet(NestedViewSet):
    view_name = 'Note'
    lookup_field = 'ext_id'
    queryset = Note.objects.all()
    serializer_class = serializers.NoteSerializer

    search_fields = ('title', 'text')
    ordering_fields = ('created', 'updated', 'title')

    parent_model = Notebook

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_note_serializer_class)

    def get_view_name(self):
        name = self.view_name
        if self.suffix:
            name += ' ' + self.suffix
        return name


class NoteViewSet(BaseNoteViewSet):
    safe_parent = False

    object_filters = {
        'notebook__user_id': 'user_username',
        'notebook_id': 'notebook_ext_id'
    }
    parent_filters = {
        'user_id': 'user_username',
        'ext_id': 'notebook_ext_id'
    }


class UserNoteViewSet(BaseNoteViewSet):
    # TODO: remove unsafe methods
    safe_parent = True

    object_filters = {'notebook__user_id': 'user_username'}
    parent_filters = {'user_id': 'user_username'} # TODO: maybe remove this to avoid masking errors from unsafe methods

# TODO: prefix private mixin method names with underscores
# TODO: check for unnecessary code in .rest.fields
