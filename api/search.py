from django.conf import settings
from django.db.models import TextField
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import decorators

import util


class SearchableModelMixin(object):
    SEARCH_PARAM = 'q'
    full_text_vector = ()

    def add_timeframed_action(self):
        timeframed_actions = getattr(self, 'timeframed_actions', ())
        timeframed_actions += (self.action,)
        setattr(self, 'timeframed_actions', timeframed_actions)

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

    def get_queryset(self):
        queryset = super(SearchableModelMixin, self).get_queryset()

        terms = ' '.join(self.request.query_params.getlist(self.SEARCH_PARAM))

        if util.is_pgsql() and settings.API_SEARCH_USE_TRIGRAM:
            search_func = self.search_trigram_similarity
        else:
            search_func = self.search_basic

        queryset = search_func(queryset, terms)

        return queryset

    @decorators.list_route()
    def search(self, request, *args, **kwargs):
        self.add_timeframed_action()
        return self.list(request, *args, **kwargs)
