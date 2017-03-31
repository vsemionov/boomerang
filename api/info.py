from collections import OrderedDict
from rest_framework import viewsets, mixins, response, reverse


NAME = 'vsemionov.boomerang.api'
VERSION = '0.5.14'


class ApiInfoViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    view_name = 'Api Info'

    @staticmethod
    def _get_user_url(request):
        return request.user.id and reverse.reverse('user-detail', request=request, args=[request.user.username])

    def get_view_name(self):
        return self.view_name

    def list(self, request, *args, **kwargs):
        app = OrderedDict((('name', NAME),
                           ('version', VERSION)))
        user = OrderedDict((('username', request.user.username),
                            ('url', self._get_user_url(request))))
        info = OrderedDict((('app', app),
                            ('user', user)))
        return response.Response(info)
