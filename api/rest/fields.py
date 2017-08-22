import uuid

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class SecondaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, *args, **kwargs):
        kwargs['pk_field'] = serializers.UUIDField(format='hex')
        self.optimized = 'source' in kwargs
        super(SecondaryKeyRelatedField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        try:
            return self.get_queryset().get(ext_id=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        if self.pk_field is not None:
            return self.pk_field.to_representation(value.ext_id)
        return value.ext_id

    def use_pk_only_optimization(self):
        return self.optimized


class DynamicHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def __init__(self, parent_lookup=None, aux_lookup=None, *args, **kwargs):
        super(DynamicHyperlinkedIdentityField, self).__init__(*args, **kwargs)

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
