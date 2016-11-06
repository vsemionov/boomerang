import itertools
from collections import OrderedDict
from django.db.models import Value, TextField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import filters

import util
from mixins import ViewSetMixin


class SearchFilter(filters.SearchFilter):
    def get_search_terms(self, request):
        params = ' '.join(request.query_params.getlist(self.search_param))
        return params.replace(',', ' ').split()


class SearchableModelMixin(ViewSetMixin):
    SEARCH_PARAM = 'q'

    search_fields = ()

    def __init__(self, *args, **kwargs):
        super(SearchableModelMixin, self).__init__(*args, **kwargs)

        self.terms = None

        self.full_text_search = False

        self.full_text_vector = sum(itertools.izip_longest(self.search_fields, (), fillvalue=Value(' ')), ())
        if len(self.search_fields) > 1:
            self.full_text_vector = self.full_text_vector[:-1]

        self.search_filter = SearchFilter()
        self.search_filter.search_param = self.SEARCH_PARAM

    def get_full_text_expr(self):
        return Concat(*self.full_text_vector, output_field=TextField())

    def search_basic(self, queryset):
        return self.search_filter.filter_queryset(self.request, queryset, self)

    def search_trigram_similarity(self, queryset):
        full_text_expr = self.get_full_text_expr()
        similarity = TrigramSimilarity(full_text_expr, self.terms)
        queryset = queryset.annotate(rank=similarity)
        queryset = queryset.filter(rank__gt=0)
        queryset = queryset.order_by('-rank', 'created', 'id')
        return queryset

    def search_queryset(self, queryset):
        if self.full_text_search and util.is_pgsql():
            search_func = self.search_trigram_similarity
        else:
            search_func = self.search_basic

        queryset = search_func(queryset)

        return queryset

    def get_queryset(self):
        queryset = self.get_chain_queryset(SearchableModelMixin)

        if self.terms:
            queryset = self.search_queryset(queryset)

        return queryset

    get_base_queryset = get_queryset

    def list(self, request, *args, **kwargs):
        if SearchableModelMixin in self.disabled_mixins:
            return super(SearchableModelMixin, self).list(request, *args, **kwargs)

        query_terms = request.query_params.getlist(self.SEARCH_PARAM)
        self.terms = ' '.join(query_terms) if query_terms else None

        data = OrderedDict(terms=self.terms)

        return self.decorated_base_list(SearchableModelMixin, data, request, *args, **kwargs)
