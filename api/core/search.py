import itertools
from collections import OrderedDict

from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import filters

from .mixin import ViewSetMixin


DEFAULT_SEARCH_PARAM = 'q'


class SearchFilter(filters.SearchFilter):
    search_param = DEFAULT_SEARCH_PARAM

    def get_search_terms(self, request):
        params = ' '.join(request.query_params.getlist(self.search_param))
        return params.replace(',', ' ').split()


class SearchableModelMixin(ViewSetMixin):
    SEARCH_PARAM = DEFAULT_SEARCH_PARAM

    search_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.explicit_search = False

        self.terms = None

        self.full_text_search = False

    def _search_basic(self, queryset):
        search_filter = SearchFilter()
        search_filter.search_param = self.SEARCH_PARAM
        return search_filter.filter_queryset(self.request, queryset, self)

    def _search_trigram_similarity(self, queryset):
        full_text_vector = sum(itertools.zip_longest(self.search_fields, (), fillvalue=Value(' ')), ())
        if len(self.search_fields) > 1:
            full_text_vector = full_text_vector[:-1]

        full_text_expr = Concat(*full_text_vector, output_field=TextField())

        similarity = TrigramSimilarity(full_text_expr, self.terms)

        queryset = queryset.annotate(rank=similarity)
        queryset = queryset.filter(rank__gt=0)
        queryset = queryset.order_by('-rank')
        return queryset

    def _search_queryset(self, queryset):
        if self.full_text_search:
            search_func = self._search_trigram_similarity
        else:
            search_func = self._search_basic

        queryset = search_func(queryset)

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.explicit_search and self.terms:
            queryset = self._search_queryset(queryset)

        return queryset

    def list(self, request, *args, **kwargs):
        query_terms = request.query_params.getlist(self.SEARCH_PARAM)
        self.terms = ' '.join(query_terms) if query_terms else None

        data = OrderedDict(terms=self.terms)

        return self.decorated_base_list(SearchableModelMixin, data, request, *args, **kwargs)
