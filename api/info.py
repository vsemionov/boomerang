from collections import OrderedDict
from rest_framework import viewsets, mixins, response, reverse


NAME = 'vsemionov.boomerang.api'
VERSION = '0.5.5'


class InfoViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    view_name = 'Info'

    @staticmethod
    def _get_user_url(request):
        return request.user.id and reverse.reverse('user-detail', request=request, args=[request.user.username])

    def get_view_name(self):
        return self.view_name

    def list(self, request, *args, **kwargs):
        from django.core.cache import caches
        import time
        THROTTLE_CACHE_ALIAS = 'api_throttle'
        throttle_cache = caches[THROTTLE_CACHE_ALIAS]
        t0 = time.time()
        o = throttle_cache.get('throttle_user_3')
        t = time.time() - t0
        if o:
            print("cache found in %f s" % t)
        else:
            print("cache not found")
        app = OrderedDict((('name', NAME),
                           ('version', VERSION)))
        user = OrderedDict((('username', request.user.username),
                            ('url', self._get_user_url(request))))
        info = OrderedDict((('app', app),
                            ('user', user)))
        return response.Response(info)
