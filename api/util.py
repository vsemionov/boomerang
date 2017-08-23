from django.core.exceptions import FieldDoesNotExist
from rest_framework_jwt.settings import api_settings


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def get_view_description(cls, html=False):
    return ''


def is_deletable(model):
    try:
        model._meta.get_field('deleted')
    except FieldDoesNotExist:
        return False

    return True


def create_jwt(user):
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token
