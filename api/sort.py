from collections import OrderedDict

from mixins import ViewSetMixin


class SortedModelMixin(ViewSetMixin):
    SORT_PARAM = 'sort'
    DEFAULT_SORT = ('created',)
    SORT_FIELD_MAP = {
        'id': 'ext_id',
        '-id': '-ext_id',
    }

    def __init__(self, *args, **kwargs):
        super(SortedModelMixin, self).__init__(*args, **kwargs)

        self.sort = None

    def get_queryset(self):
        queryset = self.get_chain_queryset(SortedModelMixin)

        if self.sort:
            queryset = queryset.order_by(*self.sort)

        return queryset

    get_base_queryset = get_queryset

    def translated_sort(self, sort):
        return tuple(self.SORT_FIELD_MAP.get(field, field) for field in sort)

    def consistent_sort(self, sort):
        return sort + ('id',)

    def list(self, request, *args, **kwargs):
        if SortedModelMixin in self.disabled_mixins:
            return super(SortedModelMixin, self).list(request, *args, **kwargs)

        sort_args = request.query_params.getlist(self.SORT_PARAM)
        sort_order = ','.join([sort_arg.replace(' ', '') for sort_arg in sort_args])
        self.sort = tuple(sort_order.split(',')) if sort_order else self.DEFAULT_SORT

        data = OrderedDict(sort=','.join(self.sort))

        self.sort = self.translated_sort(self.sort)
        self.sort = self.consistent_sort(self.sort)

        return self.decorated_base_list(SortedModelMixin, data, request, *args, **kwargs)
