from collections import OrderedDict
from rest_framework import response


class ViewSetMixin(object):
    _queryset = None

    @property
    def queryset(self):
        if self._queryset is None:
            self._queryset = self.get_base_queryset()
        return self._queryset

    def get_base_queryset(self):
        raise NotImplementedError()

    def decorated_base_list(self, cls, data, request, *args, **kwargs):
        base_response = super(cls, self).list(request, *args, **kwargs)
        base_data = base_response.data
        data.update(base_data)
        return response.Response(data)
