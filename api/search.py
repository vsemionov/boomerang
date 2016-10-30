from collections import OrderedDict
from django.conf import settings
from django.db.models import TextField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import response

import util


class SearchableModelMixin(object):
    SEARCH_PARAM = 'q'
    full_text_vector = ()

    def __init__(self, *args, **kwargs):
        self.terms = None
        super(SearchableModelMixin, self).__init__(*args, **kwargs)

    def get_full_text_expr(self):
        return Concat(*self.full_text_vector, output_field=TextField())

    def search_basic(self, queryset, terms):
        full_text_expr = self.get_full_text_expr()
        full_text_qs = queryset.annotate(full_text=full_text_expr)
        return full_text_qs.filter(full_text__icontains=terms)

    def search_trigram_similarity(self, queryset, terms):
        full_text_expr = self.get_full_text_expr()
        similarity = TrigramSimilarity(full_text_expr, terms)
        return queryset.annotate(rank=similarity).order_by('-rank')

    def search_queryset(self, queryset, terms):
        if util.is_pgsql() and settings.API_SEARCH_USE_TRIGRAM:
            search_func = self.search_trigram_similarity
        else:
            search_func = self.search_basic

        queryset = search_func(queryset, terms)

        return queryset

    def get_queryset(self):
        super_proxy = super(SearchableModelMixin, self)
        if hasattr(super_proxy, 'get_base_queryset'):
            proxy = super_proxy
        else:
            proxy = self
        queryset = proxy.get_base_queryset()

        if self.action != 'list' or not self.terms:
            return queryset

        terms = ' '.join(self.request.query_params.getlist(self.SEARCH_PARAM))

        queryset = self.search_queryset(queryset, terms)

        return queryset

    get_base_queryset = get_queryset

    def list(self, request, *args, **kwargs):
        qterms = self.request.query_params.getlist(self.SEARCH_PARAM)
        self.terms = ' '.join(qterms) if qterms else None

        base_response = super(SearchableModelMixin, self).list(request, *args, **kwargs)
        base_data = base_response.data
        assert isinstance(base_data, OrderedDict), 'unexpected response data type'

        data = OrderedDict(terms=self.terms)
        data.update(base_data)

        return response.Response(data)
