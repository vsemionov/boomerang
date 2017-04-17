from collections import OrderedDict

from rest_framework import viewsets, mixins, permissions, response, reverse

from .util import create_jwt


class JWTViewSet(mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    view_name = 'JWT'
    permission_classes = (permissions.IsAuthenticated,)

    @staticmethod
    def _get_user_url(request):
        return reverse.reverse('user-detail', request=request, args=[request.user.username])

    def get_view_name(self):
        return self.view_name

    def list(self, request, *args, **kwargs):
        user = request.user
        token = create_jwt(user)
        jwt = OrderedDict((('username', user.username),
                           ('token', token)))
        return response.Response(jwt)
