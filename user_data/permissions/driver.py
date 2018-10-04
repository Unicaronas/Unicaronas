from rest_framework.permissions import BasePermission


class UserIsDriver(BasePermission):
    """User is a driver"""

    def has_permission(self, request, view):
        return hasattr(request.user, 'driver')
