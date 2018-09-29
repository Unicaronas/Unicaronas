from rest_framework import permissions


class IsReadyOnlyRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsPostRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == "POST"


class IsGetRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == "GET"


class IsPutPatchRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == "PUT" or request.method == "PATCH"


class IsDeleteRequest(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.method == "DELETE"
