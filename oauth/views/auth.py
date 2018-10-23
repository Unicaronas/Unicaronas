from oauth2_provider.scopes import get_scopes_backend
from oauth2_provider.models import get_access_token_model
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from ..serializers import DebugTokenSerializer
from ..forms import CustomAllowForm
from .pkce_auth import PKCEAuthorizationView


class CustomAuthorizationView(PKCEAuthorizationView):
    """Custom Auth

    Custom auth view that lets users select which permissions to allow
    - Limits permissons to the ones requested by the app during signup
    """
    form_class = CustomAllowForm

    def get_initial(self):
        initial_data = super().get_initial()
        all_scopes = get_scopes_backend().get_all_scopes()
        initial_data["scope_choices"] = str([(s_name, all_scopes[s_name]) for s_name in initial_data['scope'].split()])
        return initial_data

    def get_context_data(self, *args, **kwargs):
        """
        This tells the template which scopes are default ones
        so that it can block changes to those
        """
        context = super().get_context_data(*args, **kwargs)
        context['default_scopes'] = get_scopes_backend().get_default_scopes()
        return context

    def validate_authorization_request(self, request):
        """
        By intercepting this call, I can make sure that the default scopes are
        always included in the original call
        """
        extra_scopes, credentials = super().validate_authorization_request(request)
        scopes = get_scopes_backend().get_default_scopes()
        for extra in extra_scopes:
            if extra not in scopes:
                scopes.append(extra)
        return scopes, credentials


class DebugToken(generics.RetrieveAPIView):
    """Debug Token
    Returns useful info about the token
    """
    versioning_class = None
    authentication_classes = []
    permission_classes = [IsAdminUser]
    queryset = get_access_token_model().objects.all()
    lookup_field = 'token'
    lookup_url_kwarg = 'input_token'
    serializer_class = DebugTokenSerializer
