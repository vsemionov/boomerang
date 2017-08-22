from rest_framework import response


class ViewSetMixin(object):
    disabled_mixins = set()

    def get_base_queryset(self):
        raise NotImplementedError()

    def get_queryset(self):
        return self.get_base_queryset()

    def decorated_base_list(self, cls, data, request, *args, **kwargs):
        base_response = super(cls, self).list(request, *args, **kwargs)
        base_data = base_response.data
        data.update(base_data)
        return response.Response(data)
