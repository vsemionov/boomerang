import itertools
from collections import OrderedDict
from rest_framework import filters

from mixins import ViewSetMixin


DEFAULT_SORT_PARAM = 'sort'
SORT_FIELD_MAP = {
    'id': 'ext_id',
    '-id': '-ext_id',
}


def get_sort_order(request, param):
    args = request.query_params.getlist(param)
    fields = itertools.chain(*(arg.split(',') for arg in args))
    order = tuple(field.strip() for field in fields if field)
    return order


def translated_sort(fields):
    return tuple(SORT_FIELD_MAP.get(field, field) for field in fields)


def consistent_sort(fields):
    return fields + type(fields)(('id',))


class OrderingFilter(filters.OrderingFilter):
    ordering_param = DEFAULT_SORT_PARAM

    def get_ordering(self, request, queryset, view):
        fields = get_sort_order(request, self.ordering_param)
        if fields:
            fields = translated_sort(fields)
            ordering = self.remove_invalid_fields(queryset, fields, view)
            if ordering:
                ordering = consistent_sort(ordering)
                return ordering
        return self.get_default_ordering(view)


class SortedModelMixin(ViewSetMixin):
    SORT_PARAM = DEFAULT_SORT_PARAM
    DEFAULT_SORT = ('created',)

    def __init__(self, *args, **kwargs):
        super(SortedModelMixin, self).__init__(*args, **kwargs)

        self.perform_sort = True

        self.sort = None

    def get_queryset(self):
        queryset = self.get_chain_queryset(SortedModelMixin)

        if self.sort and self.perform_sort:
            queryset = queryset.order_by(*self.sort)

        return queryset

    get_base_queryset = get_queryset

    def list(self, request, *args, **kwargs):
        if SortedModelMixin in self.disabled_mixins:
            return super(SortedModelMixin, self).list(request, *args, **kwargs)

        self.sort = get_sort_order(request, self.SORT_PARAM) or self.DEFAULT_SORT

        data = OrderedDict(sort=','.join(self.sort))

        self.sort = translated_sort(self.sort)
        self.sort = consistent_sort(self.sort)

        return self.decorated_base_list(SortedModelMixin, data, request, *args, **kwargs)
