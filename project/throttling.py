from rest_framework.throttling import SimpleRateThrottle


class ApplicationRateThrottle(SimpleRateThrottle):
    """
    Limits the rate of API calls that may be made by a given application.

    The application id will be used as a unique cache key if the call was made
    through OAuth2.
    """
    scope = 'application'

    def get_cache_key(self, request, view):
        if getattr(request, 'auth', None) is not None:
            ident = request.auth.application.id
        else:
            return None  # Only throttle applications

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }


class ApplicationBurstRateThrottle(ApplicationRateThrottle):
    """
    Limits the burst rate of API calls that may be made by a given application.
    """
    scope = 'application_burst'


class ApplicationSustainedRateThrottle(ApplicationRateThrottle):
    """
    Limits the sustained rate of API calls that may be made by a given application.
    """
    scope = 'application_sustained'
