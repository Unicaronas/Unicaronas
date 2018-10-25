import requests
from urllib.parse import urlencode

from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404, reverse
from django.http import Http404
from django.utils import timezone

from .models import FacebookGroup


def get_search_keys():
    return ['facebook', 'blablacar']


def get_fb_groups_ids():
    return [group.id for group in FacebookGroup.objects.filter(expires__gt=timezone.now())]


def get_search_values():
    from .search import FacebookSearch, BlaBlaCarSearch
    fb_groups = [FacebookSearch(group) for group in get_fb_groups_ids()]
    return [fb_groups, BlaBlaCarSearch()]


def get_search_map():
    keys = get_search_keys()
    values = get_search_values()
    return {keys[i]: values[i] for i in range(len(keys))}


def get_client_info(request):
    user = request.user
    fb_group_id = request.session.get('fb_group_id', None)

    fb_group = get_object_or_404(FacebookGroup, id=fb_group_id, user=user)

    client_id = fb_group.client_id
    client_secret = fb_group.client_secret
    return client_id, client_secret


def get_redirect_uri(request):
    if request.is_secure():
        redirect_uri = 'https://' + request.get_host() + reverse('third_parties:fb_group_callback')
    else:
        redirect_uri = 'https://' + request.get_host() + reverse('third_parties:fb_group_callback')
    return redirect_uri


def get_fb_login_url(request):
    client_id, _ = get_client_info(request)
    redirect_uri = get_redirect_uri(request)
    url = "https://www.facebook.com/dialog/oauth?"
    kvps = {'client_id': client_id, 'redirect_uri': redirect_uri}
    kvps['state'] = request.session.get('fb_state', get_random_string())
    request.session['fb_state'] = kvps['state']
    kvps['scope'] = ",".join(['publish_to_groups', 'groups_access_member_info'])

    return url + urlencode(kvps)


def extend_token(client_id, client_secret, token):
    url = 'https://graph.facebook.com/oauth/access_token?'
    kvps = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'fb_exchange_token',
        'fb_exchange_token': token
    }
    url += urlencode(kvps)
    return requests.get(url).json()['access_token']


def exchange_code(request, code, state):
    client_id, client_secret = get_client_info(request)
    p_state = request.session.get('fb_state', '')
    if p_state != state:
        raise Http404

    redirect_uri = get_redirect_uri(request)
    url = 'https://graph.facebook.com/oauth/access_token?'
    kvps = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code
    }

    url += urlencode(kvps)
    response = requests.get(url)
    r_json = response.json()
    access_token = r_json['access_token']

    ll_access_token = extend_token(client_id, client_secret, access_token)

    return ll_access_token
