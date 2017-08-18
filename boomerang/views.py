from django.views.generic.base import RedirectView
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect


def redirect_internal(view_name, query=False):
    return RedirectView.as_view(pattern_name=view_name, query_string=query)


def redirect_arbitrary(request):
    try:
        url = request.GET['to']
    except KeyError:
        return HttpResponseBadRequest()

    if url not in settings.REDIRECT_ALLOWED_URLS:
        return HttpResponseBadRequest()

    return redirect(url)
