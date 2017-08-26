from django.shortcuts import get_object_or_404

from .mixin import ViewSetMixin
from .util import is_deletable


class NestedModelMixin(ViewSetMixin):

    parent_model = None
    safe_parent = False # set to false if the parent url argument has been verified (e.g. by permissions)

    object_filters = {}
    parent_filters = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.deleted_parent = False

    def get_parent_name(self):
        return self.parent_model._meta.model_name

    def _filter_queryset(self, queryset, filters, is_parent):
        filter_kwargs = {expr: self.kwargs[kwarg] for expr, kwarg in filters.items()}

        if self.deleted_parent is not None:
            if is_deletable(self.parent_model):
                expr = 'deleted' if is_parent else self.get_parent_name() + '__deleted'
                filter_kwargs.update({expr: self.deleted_parent})

        queryset = queryset.filter(**filter_kwargs)
        return queryset

    def get_parent_queryset(self):
        queryset = self.parent_model.objects
        queryset = self._filter_queryset(queryset, self.parent_filters, True)
        return queryset

    def get_parent(self):
        queryset = self.get_parent_queryset()
        parent = get_object_or_404(queryset)
        return parent

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self._filter_queryset(queryset, self.object_filters, False)
        return queryset

    def list(self, request, *args, **kwargs):
        if not self.safe_parent:
            self.get_parent()
        return super().list(request, *args, **kwargs)


class ReadWriteNestedModelMixin(NestedModelMixin):

    def update(self, request, *args, **kwargs):
        self.deleted_parent = None
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.deleted_parent = None
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        parent = self.get_parent()
        serializer.save(**{self.get_parent_name(): parent})
