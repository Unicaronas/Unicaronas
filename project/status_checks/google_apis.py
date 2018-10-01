from django.conf import settings
from search.geocoding import geocode_address
from watchman.decorators import check


@check
def _geocode_address():
    geocode_address('Unicamp')
    return {'Geocoding': {'ok': True}}


def google_apis():
    if not settings.WATCHMAN_ENABLE_PAID_CHECKS:
        return {}
    return {'Google APIs': [_geocode_address()]}
