import django_filters
from django_filters.rest_framework import FilterSet

from .models import Notebook, Note, Task


class NotebookFilter(FilterSet):
    created_since = django_filters.IsoDateTimeFilter(name='created', lookup_expr='gte')
    created_until = django_filters.IsoDateTimeFilter(name='created', lookup_expr='lt')
    updated_since = django_filters.IsoDateTimeFilter(name='updated', lookup_expr='gte')
    updated_until = django_filters.IsoDateTimeFilter(name='updated', lookup_expr='lt')

    class Meta:
        model = Notebook
        fields = ('created_since', 'created_until', 'updated_since', 'updated_until')


class NoteFilter(FilterSet):
    created_since = django_filters.IsoDateTimeFilter(name='created', lookup_expr='gte')
    created_until = django_filters.IsoDateTimeFilter(name='created', lookup_expr='lt')
    updated_since = django_filters.IsoDateTimeFilter(name='updated', lookup_expr='gte')
    updated_until = django_filters.IsoDateTimeFilter(name='updated', lookup_expr='lt')

    class Meta:
        model = Note
        fields = ('created_since', 'created_until', 'updated_since', 'updated_until')


class TaskFilter(FilterSet):
    created_since = django_filters.IsoDateTimeFilter(name='created', lookup_expr='gte')
    created_until = django_filters.IsoDateTimeFilter(name='created', lookup_expr='lt')
    updated_since = django_filters.IsoDateTimeFilter(name='updated', lookup_expr='gte')
    updated_until = django_filters.IsoDateTimeFilter(name='updated', lookup_expr='lt')

    class Meta:
        model = Task
        fields = ('created_since', 'created_until', 'updated_since', 'updated_until', 'done')
