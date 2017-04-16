
# TODO: remove this when django-allauth issue #1701 is fixed
# see https://github.com/pennersr/django-allauth/issues/1701
class NoFbsrMiddleware:
    'removes facebook fbsr_ cookies'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cookies = []
        for cookie in request.COOKIES:
            if cookie.startswith("fbsr_"):
                cookies.append(cookie)

        response = self.get_response(request)

        for cookie in cookies:
            response.set_cookie(cookie)

        return response
