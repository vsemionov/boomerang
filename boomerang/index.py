import os

from django.conf import settings
from django.http import FileResponse
from django.contrib.staticfiles import finders

from api.util import create_jwt


def index(request):
    relpath = os.path.join('web', 'index.html')
    if settings.DEBUG:
        abspath = finders.find(relpath)
    else:
        abspath = os.path.join(settings.STATIC_ROOT, relpath)
    response = FileResponse(open(abspath, 'rb'), content_type='text/html; charset=utf-8')
    if request.user and request.user.is_authenticated:
        token = create_jwt(request.user)
        response.set_cookie('jwt', token)
    return response
