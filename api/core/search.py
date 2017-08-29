import itertools
from collections import OrderedDict

from django.db.models import Value, TextField, FloatField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import filters, decorators

from .mixin import ViewSetMixin


DEFAULT_SEARCH_PARAM = 'q'


class SearchFilter(filters.SearchFilter):
    search_param = DEFAULT_SEARCH_PARAM

    def get_search_terms(self, request):
        params = ' '.join(request.query_params.getlist(self.search_param))
        return params.replace(',', ' ').split()

    def filter_queryset(self, request, queryset, view):
        if view.full_text_search:
            return queryset

        return super().filter_queryset(request, queryset, view)


class SearchableModelMixin(ViewSetMixin):
    SEARCH_PARAM = DEFAULT_SEARCH_PARAM

    search_fields = ()

    full_text_search = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.terms = None

    def _search_queryset(self, queryset):
        full_text_vector = sum(itertools.zip_longest(self.search_fields, (), fillvalue=Value(' ')), ())
        if len(self.search_fields) > 1:
            full_text_vector = full_text_vector[:-1]

        full_text_expr = Concat(*full_text_vector, output_field=TextField())

        similarity = TrigramSimilarity(full_text_expr, self.terms)

        queryset = queryset.annotate(rank=similarity)
        queryset = queryset.filter(rank__gt=0)

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.full_text_search and self.terms:
            queryset = self._search_queryset(queryset)
        else:
            queryset = queryset.annotate(rank=Value(1.0, output_field=FloatField()))

        return queryset

    def list(self, request, *args, **kwargs):
        query_terms = request.query_params.getlist(self.SEARCH_PARAM)

        self.terms = ' '.join(query_terms) if query_terms else None

        context = OrderedDict(terms=self.terms)

        return self.decorated_list(SearchableModelMixin, context, request, *args, **kwargs)

    @decorators.list_route(suffix='Search')
    def search(self, request, *args, **kwargs):
        self.ordering_fields = ('rank',) + self.__class__.ordering_fields
        self.ordering = ('-rank',) + self.__class__.ordering

        self.full_text_search = True

        return self.list(request, *args, **kwargs)
