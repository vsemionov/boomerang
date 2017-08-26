import uuid

from rest_framework import serializers


class DynamicHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def __init__(self, parent_lookup=None, aux_lookup=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent_lookup = parent_lookup or {}
        self.aux_lookup = aux_lookup or {}

    def get_url(self, obj, view_name, request, format):
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        kwargs.update(self.parent_lookup)
        kwargs.update({kwarg: getattr(obj, field) for (kwarg, field) in self.aux_lookup.items()})

        for key in kwargs:
            value = kwargs[key]
            if isinstance(value, uuid.UUID):
                kwargs[key] = value.hex

        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
