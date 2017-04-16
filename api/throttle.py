from django.core.cache import caches
from rest_framework import throttling


THROTTLE_CACHE_ALIAS = 'api_throttle'


# django caches are thread local, including their connection pools
# therefore, different threads cannot reuse each other's connections
# this cache and its connection pool are created at import time and are therefore global
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
