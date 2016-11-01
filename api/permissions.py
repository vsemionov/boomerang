from rest_framework import permissions


class UserPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'list':
            return True
        else:
            return str(request.user.username) == view.kwargs['username'] or \
                   (request.user.is_staff and request.method in permissions.SAFE_METHODS)


class NestedPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return str(request.user.username) == view.kwargs['user_username'] or \
               (request.user.is_staff and request.method in permissions.SAFE_METHODS)


user_permissions = (permissions.IsAuthenticated, UserPermissions)
nested_permissions = (permissions.IsAuthenticated, NestedPermissions)
