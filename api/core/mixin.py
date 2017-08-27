from rest_framework import response


class ViewSetMixin(object):

    def get_queryset(self):
        return self.queryset

    def decorated_base_list(self, cls, data, request, *args, **kwargs):
        base_response = super(cls, self).list(request, *args, **kwargs)

        data.update(base_response.data)

        return response.Response(data)
