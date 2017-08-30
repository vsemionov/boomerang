from collections import OrderedDict

from rest_framework import response


class ViewSetMixin(object):

    def get_queryset(self):
        return self.queryset

    def decorated_list(self, cls, context, request, *args, **kwargs):
        base_response = super(cls, self).list(request, *args, **kwargs)

        if isinstance(base_response.data, dict):
            base_data = base_response.data
        else:
            base_data = OrderedDict(results=base_response.data)

        data = context.copy()
        data.update(base_data)

        return response.Response(data)
