from collections import OrderedDict
from rest_framework import viewsets, mixins, response, reverse
from django.conf import settings


class ApiInfoViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    view_name = 'Api Info'

    @staticmethod
    def _get_user_url(request):
        return reverse.reverse('user-detail', request=request, args=[request.user.username])

    def get_view_name(self):
        return self.view_name

    def list(self, request, *args, **kwargs):
        app = OrderedDict((('name', settings.PROJECT_NAME),
                           ('version', settings.PROJECT_VERSION)))
        user = OrderedDict((('username', request.user.username),
                            ('url', self._get_user_url(request)))) \
            if request.user.id else None
        info = OrderedDict((('app', app),
                            ('user', user)))
        return response.Response(info)
