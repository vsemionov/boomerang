from collections import OrderedDict

from rest_framework import viewsets, mixins, permissions, response
from rest_framework.authtoken.models import Token


class TokenViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    view_name = 'Token'
    permission_classes = (permissions.IsAuthenticated,)

    def get_view_name(self):
        return self.view_name

    @staticmethod
    def create_token(user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    def list(self, request, *args, **kwargs):
        user = request.user

        token = self.create_token(user)

        token = OrderedDict((('username', user.username),
                             ('token', token)))

        return response.Response(token)
