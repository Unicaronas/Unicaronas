from django.conf import settings


def fb_handle(request):
    return {'facebookHandle': settings.FACEBOOK_HANDLE}
