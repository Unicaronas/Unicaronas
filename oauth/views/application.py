from rest_framework import viewsets
from oauth2_provider.models import get_application_model
from ..serializers import ApplicationListSerializer, ApplicationDetailSerializer
from ..mixins import ApplicationOwnerIsUserMixin


class ApplicationViewset(ApplicationOwnerIsUserMixin, viewsets.ModelViewSet):
    """ Application Viewset

    Requires session or oauth token with specific permissions

    list:
    If session, lists all saved Applications. Allows filtering. If oauth, lists only the user's Applications

    create:
    Create a new Application. Links current user as the owner.

    retrieve:
    Direct link to the Application. Displays credentials

    update:
    Updates Application' info.

    partial_update:
    Updates Application' info.

    delete:
    Deletes an Application
    """

    serializer_class = ApplicationDetailSerializer
    lookup_field = 'client_id'

    serializer_action_classes = {
        'list': ApplicationListSerializer,
        'create': ApplicationDetailSerializer
    }

    queryset = get_application_model().objects.all()

    def get_serializer_class(self):
        """User list and create serialize for list and create views"""
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def perform_create(self, serializer):
        # Overrides perform_create to set user as current user
        serializer.save(user=self.request.user)
