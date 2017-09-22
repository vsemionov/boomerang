from collections import OrderedDict

from rest_framework import viewsets, mixins, permissions, response, reverse
from rest_framework.settings import api_settings as rest_settings
from rest_framework_jwt.settings import api_settings as jwt_settings
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


jwt_payload_handler = jwt_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = jwt_settings.JWT_ENCODE_HANDLER


def create_jwt(user):
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


class JWTViewSet(mixins.ListModelMixin,
                 viewsets.GenericViewSet):
    view_name = 'JWT'
    authentication_classes = tuple(cls for cls in rest_settings.DEFAULT_AUTHENTICATION_CLASSES
                                   if cls is not JSONWebTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_view_name(self):
        return self.view_name

    def list(self, request, *args, **kwargs):
        user = request.user

        token = create_jwt(user)

        jwt = OrderedDict((('username', user.username),
                           ('token', token)))

        return response.Response(jwt)
