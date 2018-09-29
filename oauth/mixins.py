from oauth2_provider.models import get_application_model
from .permissions import IsAuthenticatedOrTokenHasResourceScope


class ApplicationOwnerIsUserMixin():
    """
    This mixin is used to provide an Application queryset filtered by the current request.user.

    The current request.user is the resource owner. i.e., who authorized the app
    """
    permission_classes = [IsAuthenticatedOrTokenHasResourceScope]
    required_scopes = ['manage_apps']

    def get_queryset(self):
        return get_application_model().objects.filter(user=self.request.user)
