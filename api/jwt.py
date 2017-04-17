from collections import OrderedDict

from rest_framework import viewsets, mixins, permissions, response, reverse
from rest_framework_jwt.settings import api_settings


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


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

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        jwt = OrderedDict((('username', user.username),
                           ('token', token)))

        return response.Response(jwt)
