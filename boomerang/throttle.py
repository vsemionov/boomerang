from django.core.cache import caches
from rest_framework import throttling


THROTTLE_CACHE_ALIAS = 'api_throttle'


throttle_cache = caches[THROTTLE_CACHE_ALIAS]


class UserRateThrottle(throttling.UserRateThrottle):
    cache = throttle_cache


class HostRateThrottle(throttling.SimpleRateThrottle):
    cache = throttle_cache
    scope = 'host'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
