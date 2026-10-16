from rest_framework.permissions import BasePermission
from apps.users.models import User


class CanAccessTicket(BasePermission):
    """
    Object-level access:
    - Customer can access only their own tickets.
    - Agent can access tickets assigned to them or their team.
    - Manager and Admin can access any ticket.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role in [User.Role.ADMIN, User.Role.MANAGER]:
            return True

        if user.role == User.Role.CUSTOMER:
            return obj.customer_id == user.id

        if user.role == User.Role.AGENT:
            return (
                obj.assigned_agent_id == user.id
                or (obj.assigned_team_id and obj.assigned_team_id == user.team_id)
                or obj.assigned_team_id is None
            )

        return False