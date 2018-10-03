from django.views.generic import RedirectView
from django.contrib import messages
from django.shortcuts import get_object_or_404, Http404
from django.urls import reverse_lazy
from .models import FacebookGroup
from .utils import exchange_code, get_fb_login_url


class FacebookGroupTokenBegin(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        fb_group_id = kwargs['id']
        if not self.request.user.is_authenticated:
            raise Http404
        get_object_or_404(FacebookGroup, id=fb_group_id, user=self.request.user)
        self.request.session['fb_group_id'] = fb_group_id
        return get_fb_login_url(self.request)


class FacebookGroupTokenUpdate(RedirectView):
    permanent = True
    url = reverse_lazy('profile')

    def get_redirect_url(self, *args, **kwargs):
        request = self.request
        code = self.request.GET.get('code', False)
        state = self.request.GET.get('state', '')
        if not code:
            messages.add_message(request, messages.ERROR, 'Ocorreu um erro atualizando o token da página!')
            return super().get_redirect_url(self, *args, **kwargs)
        user = request.user
        fb_group_id = request.session.get('fb_group_id', None)
        fb_group = get_object_or_404(FacebookGroup, id=fb_group_id, user=user)
        token = exchange_code(request, code, state)
        fb_group.update_token(token)
        messages.add_message(request, messages.SUCCESS, 'Token atualizado!')
        del request.session['fb_group_id']
        del request.session['fb_state']
        return super().get_redirect_url(self, *args, **kwargs)
