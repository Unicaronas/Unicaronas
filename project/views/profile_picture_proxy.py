import mimetypes
import requests
from django.http import HttpResponse, Http404
from django.views.generic import View
from django.conf import settings
from oauth2_provider.models import get_application_model
from oauth.exceptions import InvalidScopedUserId
from search.finder import RedisFinder


class PictureProxyView(View):

    picture_sizes = {
        'small_32': "profile.picture.thumbnail['32x32']",
        'small_64': "profile.picture.thumbnail['64x64']",
        'medium_128': "profile.picture.thumbnail['128x128']",
        'medium_256': "profile.picture.thumbnail['256x256']",
        'large_512': "profile.picture.thumbnail['512x512']",
        'large_1024': "profile.picture.thumbnail['1024x1024']",
        'original': "profile.picture",
    }

    @property
    def content_type(self):
        mimetype = "image/png"
        try:
            mimetype = mimetypes.guess_type(self.proxy_url)[0] or mimetype
        except Exception as e:
            raise Http404
        return mimetype

    @property
    def proxy_url(self):
        try:
            user = get_application_model().recover_scoped_user_id(self.kwargs['user_id'])
        except InvalidScopedUserId:
            raise Http404
        profile = user.profile
        profile
        try:
            return eval(self.picture_sizes.get(self.request.GET.get('size'), self.picture_sizes['medium_256'])).url
        except Exception:
            raise Http404

    def get(self, request, *args, **kwargs):
        cache_url = request.get_full_path()
        cache = RedisFinder(timeout=60 * 60 * 24)
        res = cache.get_key(cache_url)
        if res:
            return res

        url = self.proxy_url
        if url.startswith('/'):
            url = settings.ROOT_URL + url

        response = requests.get(url)
        if not response.ok:
            raise Http404
        content = response.content
        mimetype = self.content_type
        res = HttpResponse(content, content_type=mimetype)
        cache.set_key(cache_url, res)
        return res
