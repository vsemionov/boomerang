from rest_framework import response


class ViewSetMixin(object):

    def get_queryset(self):
        return self.queryset

    def decorated_list(self, cls, context, request, *args, **kwargs):
        base_response = super(cls, self).list(request, *args, **kwargs)

        data = context.copy()
        data.update(base_response.data)

        return response.Response(data)
