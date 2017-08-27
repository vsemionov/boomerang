import datetime

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count, Min
from rest_framework import viewsets, mixins, decorators, status

from .models import Notebook, Note, Task
from .rest import serializers, links
from .core import sync, nest, limit, search, sort
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
    ordering = sort.consistent_sort(('date_joined',))

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(id=self.request.user.id)

        return queryset


class NestedViewSet(sort.SortedModelMixin,
                    search.SearchableModelMixin,
                    limit.LimitedModelMixin,
                    nest.ReadWriteNestedModelMixin,
                    sync.ReadWriteSyncedModelMixin,
                    viewsets.ModelViewSet):
    lookup_field = 'ext_id'
    permission_classes = permissions.nested_permissions

    filter_backends = (search.SearchFilter, sort.OrderingFilter)
    ordering = sort.consistent_sort(sort.SortedModelMixin.DEFAULT_SORT)

    def _is_deleted_expired_possible(self):
        if settings.API_DELETED_EXPIRY_DAYS is None:
            return False

        if self.since is None:
            return True

        return self.since < (timezone.now() - datetime.timedelta(settings.API_DELETED_EXPIRY_DAYS))

    def _is_deleted_exceeded_possible(self):
        del_limit = self.get_limit(True)
        if not del_limit:
            return False

        filter_kwargs = {expr: self.kwargs[kwarg] for expr, kwarg in self.object_filters.items()}
        filter_kwargs['deleted'] = True

        results = self.queryset.filter(**filter_kwargs)
        results = results.values(self.parent_key_filter[0])
        results = results.annotate(ndel=Count('*'), oldest=Min('updated'))
        results = results.filter(ndel__gte=del_limit, oldest__gte=self.since)

        return len(results) > 0

    def get_hyperlinked_serializer_class(self, username):
        raise NotImplementedError()

    def get_serializer_class(self):
        if self.deleted_object:
            return self.serializer_class
        else:
            return self.get_hyperlinked_serializer_class(self.kwargs['user_username'])

    @decorators.list_route(suffix='Deleted List')
    def deleted(self, request, *args, **kwargs):
        self.deleted_object = True

        response = self.list(request, *args, **kwargs)

        if self._is_deleted_expired_possible() or self._is_deleted_exceeded_possible():
            response.status_code = status.HTTP_206_PARTIAL_CONTENT

        return response

    @decorators.list_route(suffix='Search')
    def search(self, request, *args, **kwargs):
        self.explicit_search = True
        self.full_text_search = True
        self.enable_sort = False
        self.filter_backends = tuple(set(self.filter_backends).difference({sort.OrderingFilter}))
        return self.list(request, *args, **kwargs)


class UserChildViewSet(NestedViewSet):
    parent_model = User
    safe_parent = True
    object_filters = {'user_id': 'user_username'}
    parent_filters = {'username': 'user_username'}
    parent_key_filter = ('user_id', 'user_username')


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
    safe_parent = False
    object_filters = {
        'notebook__user_id': 'user_username',
        'notebook_id': 'notebook_ext_id'
    }
    parent_filters = {
        'user_id': 'user_username',
        'ext_id': 'notebook_ext_id'
    }
    parent_key_filter = ('notebook_id', 'notebook_ext_id')

    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_note_serializer_class)


class UserNoteViewSet(sort.SortedModelMixin,
                      search.SearchableModelMixin,
                      nest.NestedModelMixin,
                      sync.SyncedModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    view_name = 'Note'

    lookup_field = NoteViewSet.lookup_field
    queryset = NoteViewSet.queryset
    serializer_class = NoteViewSet.serializer_class
    permission_classes = NoteViewSet.permission_classes

    filter_backends = NoteViewSet.filter_backends
    search_fields = NoteViewSet.search_fields
    ordering_fields = NoteViewSet.ordering_fields
    ordering = NoteViewSet.ordering

    parent_model = NoteViewSet.parent_model
    safe_parent = True
    object_filters = {'notebook__user_id': 'user_username'}
    # parent_filters = {'user_id': 'user_username'}
    parent_key_filter = ('notebook_id', None)

    _get_limit = NestedViewSet.get_limit

    _is_deleted_expired_possible = NestedViewSet._is_deleted_expired_possible
    _is_deleted_exceeded_possible = NestedViewSet._is_deleted_exceeded_possible

    get_serializer_class = NestedViewSet.get_serializer_class
    get_hyperlinked_serializer_class = staticmethod(links.create_hyperlinked_note_serializer_class)

    deleted = NestedViewSet.deleted

    def get_view_name(self):
        name = self.view_name
        if self.suffix:
            name += ' ' + self.suffix
        return name
