from rest_framework.permissions import BasePermission
from apps.users.models import User


class IsCustomer(BasePermission):
    """Allows access only to authenticated customer users."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.CUSTOMER
        )


class IsAgent(BasePermission):
    """Allows access only to support agents."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.AGENT
        )


class IsManager(BasePermission):
    """Allows access only to support managers."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.MANAGER
        )


class IsAdminUserRole(BasePermission):
    """Allows access only to users with the ADMIN role or superusers."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )


class IsStaffOrSupport(BasePermission):
    """Allows access to Agents, Managers, and Admins."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [User.Role.AGENT, User.Role.MANAGER, User.Role.ADMIN]
        )