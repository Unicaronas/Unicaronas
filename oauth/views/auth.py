from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from oauth2_provider.scopes import get_scopes_backend
from oauth2_provider.models import get_access_token_model, get_refresh_token_model
from oauth2_provider.views.base import AuthorizationView
from oauth2_provider.views.generic import ProtectedResourceView
from ..serializers import DebugTokenSerializer, DebugRefreshokenSerializer
from ..forms import CustomAllowForm


class CustomAuthorizationView(AuthorizationView):
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


class IntrospectViewset(
        ProtectedResourceView,
        viewsets.GenericViewSet):
    """Introspect Token
    Returns useful info about the token

    Implements an endpoint for token introspection based
    on RFC 7662 https://tools.ietf.org/html/rfc7662

    Accepts both GET requests and POST requests
    with param or data 'token'
    """
    versioning_class = None
    permission_classes = [AllowAny]
    queryset = get_access_token_model().objects.all()
    refresh_queryset = get_refresh_token_model().objects.all()
    serializer_class = DebugTokenSerializer
    refresh_serializer_class = DebugRefreshokenSerializer
    lookup_field = 'token'

    def get_token_hint(self):
        if self.action == 'create':
            return self.request.POST.get('token_type_hint', 'access_token')
        elif self.action == 'list':
            return self.request.GET.get('token_type_hint', 'access_token')
        else:
            return ''

    def get_serializer_class(self):
        token_hint = self.get_token_hint()

        token_type_map = {
            'access_token': self.serializer_class,
            'refresh_token': self.refresh_serializer_class
        }
        return token_type_map.get(token_hint, None)

    def get_queryset(self):
        token_hint = self.get_token_hint()

        token_type_map = {
            'access_token': self.queryset,
            'refresh_token': self.refresh_queryset
        }
        return token_type_map.get(token_hint, get_access_token_model().objects.none())

    def get_object(self):
        # If request is POST, retrieve object
        # from 'token' data argument
        if self.action == 'create':
            kwarg = self.request.POST.get('token', None)
        elif self.action == 'list':
            kwarg = self.request.GET.get('token', None)
        else:
            return super().get_object()

        filter_kwargs = {'token': kwarg}

        queryset = self.filter_queryset(self.get_queryset())

        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
