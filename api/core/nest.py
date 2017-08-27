from django.db import transaction
from django.shortcuts import get_object_or_404

from .mixin import ViewSetMixin
from .models import TrackedModel


class NestedModelMixin(ViewSetMixin):

    parent_model = None
    safe_parent = False

    object_filters = {}
    parent_filters = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.deleted_parent = False

    def get_parent_name(self):
        return self.parent_model._meta.model_name

    def _filter_queryset(self, queryset, is_parent):
        filters = self.parent_filters if is_parent else self.object_filters

        filter_kwargs = {expr: self.kwargs[kwarg] for expr, kwarg in filters.items()}

        if self.deleted_parent is not None:
            if issubclass(self.parent_model, TrackedModel):
                expr = 'deleted' if is_parent else self.get_parent_name() + '__deleted'
                filter_kwargs.update({expr: self.deleted_parent})

        queryset = queryset.filter(**filter_kwargs)

        return queryset

    def get_parent_queryset(self, lock):
        queryset = self.parent_model.objects

        queryset = self._filter_queryset(queryset, True)

        if lock:
            queryset = queryset.select_for_update()

        return queryset

    def get_parent(self, lock):
        queryset = self.get_parent_queryset(lock)

        parent = get_object_or_404(queryset)

        return parent

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = self._filter_queryset(queryset, False)

        return queryset

    def list(self, request, *args, **kwargs):
        if not self.safe_parent:
            self.get_parent(False)

        return super().list(request, *args, **kwargs)


class ReadWriteNestedModelMixin(NestedModelMixin):

    def create(self, request, *args, **kwargs):
        self.deleted_parent = None
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.deleted_parent = None
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.deleted_parent = None
        return super().destroy(request, *args, **kwargs)

    @transaction.atomic(savepoint=False)
    def perform_create(self, serializer):
        parent = self.get_parent(True)
        serializer.save(**{self.get_parent_name(): parent})
