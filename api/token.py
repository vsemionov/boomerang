from collections import OrderedDict

from rest_framework import viewsets, mixins, permissions, response
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings as rest_settings
from rest_framework_jwt.settings import api_settings as jwt_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class AuthViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    view_name = None
    permission_classes = (permissions.IsAuthenticated,)

    def get_view_name(self):
        return self.view_name

    def create_token(self, user):
        raise NotImplementedError()

    def list(self, request, *args, **kwargs):
        user = request.user

        token = self.create_token(user)

        token = OrderedDict((('username', user.username),
                             ('token', token)))

        return response.Response(token)


class TokenViewSet(AuthViewSet):
    view_name = 'Token'

    def create_token(self, user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key


class JWTViewSet(AuthViewSet):
    view_name = 'JWT'
    authentication_classes = tuple(cls for cls in rest_settings.DEFAULT_AUTHENTICATION_CLASSES
                                   if cls is not JSONWebTokenAuthentication)

    jwt_payload_handler = staticmethod(jwt_settings.JWT_PAYLOAD_HANDLER)
    jwt_encode_handler = staticmethod(jwt_settings.JWT_ENCODE_HANDLER)

    def create_token(self, user):
        payload = self.jwt_payload_handler(user)
        token = self.jwt_encode_handler(payload)
        return token
