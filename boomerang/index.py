import os

from django.conf import settings
from django.http import FileResponse

from api.util import create_jwt


def index(request):
    path = os.path.join(settings.STATIC_ROOT, 'web', 'index.html')
    response = FileResponse(open(path, 'rb'), content_type='text/html; charset=utf-8')
    if request.user and request.user.is_authenticated:
        token = create_jwt(request.user)
        response.set_cookie('jwt', token)
    return response
