import itertools
from collections import OrderedDict

from rest_framework import filters, exceptions

from .mixin import ViewSetMixin


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


def reverse_translated_sort(fields):
    sort_field_reverse_map = {value: key for (key, value) in SORT_FIELD_MAP.items()}
    return tuple(sort_field_reverse_map.get(field, field) for field in fields)


def consistent_sort(fields):
    return fields + type(fields)(('id',))


class OrderingFilter(filters.OrderingFilter):
    ordering_param = DEFAULT_SORT_PARAM

    def get_ordering(self, request, queryset, view):
        fields = get_sort_order(request, self.ordering_param)

        if fields:
            fields = translated_sort(fields)
            ordering = self.remove_invalid_fields(queryset, fields, view, request)

            if len(ordering) != len(fields):
                ext_fields = reverse_translated_sort(fields)
                ext_ordering = reverse_translated_sort(ordering)

                errors = {}

                for ext_field in ext_fields:
                    if ext_field not in ext_ordering:
                        errors[ext_field] = 'unknown or disallowed field'

                raise exceptions.ValidationError(errors)

            ordering = consistent_sort(ordering)
            return ordering

        return self.get_default_ordering(view)


class SortedModelMixin(ViewSetMixin):
    SORT_PARAM = DEFAULT_SORT_PARAM
    DEFAULT_SORT = ('created',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enable_sort = True
        self.sort = None

    def list(self, request, *args, **kwargs):
        if not self.enable_sort:
            return super().list(request, *args, **kwargs)

        self.sort = get_sort_order(request, self.SORT_PARAM) or self.DEFAULT_SORT

        data = OrderedDict(sort=','.join(self.sort))

        self.sort = translated_sort(self.sort)
        self.sort = consistent_sort(self.sort)

        return self.decorated_base_list(SortedModelMixin, data, request, *args, **kwargs)
