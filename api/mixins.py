from collections import OrderedDict
from rest_framework import response


class ViewSetMixin(object):
    def get_chain_queryset(self, cls):
        super_proxy = super(cls, self)
        if hasattr(super_proxy, 'get_base_queryset'):
            proxy = super_proxy
        else:
            proxy = self
        return proxy.get_base_queryset()

    def decorated_base_list(self, cls, data, request, *args, **kwargs):
        base_response = super(cls, self).list(request, *args, **kwargs)
        base_data = base_response.data
        data.update(base_data)
        return response.Response(data)
