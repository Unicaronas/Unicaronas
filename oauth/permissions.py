from rest_framework.permissions import BasePermission, IsAuthenticated

from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import TokenHasResourceScope


class IsAuthenticatedOrTokenHasResourceScope(BasePermission):
    """Custom Permission class
    The user is authenticated using some backend or the token has the right scope
    This only returns True if the user is authenticated, but not using a token
    or using a token, and the token has the correct scope.
    * It also only allows access to safe methods if the token has access to the scope:read
    and to unsafe methods if scope:write.
    This allows people browse the browsable api's if they log in using the a non
    token bassed middleware, and let them access the api's using a rest client with a token.

    Also, if the user accesses through the Browsable api, they act as resource owners.
    If they access through the api, the token owner is the resource owner.

    So they can cast unsafe methods to their own resources, but only the allowed ones to
    the user's resources.
    """

    def has_permission(self, request, view):
        is_authenticated = IsAuthenticated().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(request.successful_authenticator, OAuth2Authentication)

        token_has_scope = TokenHasResourceScope()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(request, view)
