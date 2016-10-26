from rest_framework import throttling


class HostRateThrottle(throttling.SimpleRateThrottle):
    scope = 'host'

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
