from rest_framework import serializers
from apps.tickets.models import Ticket, TicketReply, TicketEvent, TicketAssignmentHistory
from apps.users.serializers import UserProfileSerializer


class TicketReplySerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)
    author_role = serializers.CharField(source="author.role", read_only=True)

    class Meta:
        model = TicketReply
        fields = ("id", "ticket", "author_email", "author_role", "content", "is_internal", "created_at")
        read_only_fields = ("id", "ticket", "author_email", "author_role", "created_at")


class TicketEventSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)

    class Meta:
        model = TicketEvent
        fields = ("id", "event_type", "actor_email", "old_value", "new_value", "metadata", "created_at")


class TicketAssignmentHistorySerializer(serializers.ModelSerializer):
    assigned_by_email = serializers.EmailField(source="assigned_by.email", read_only=True)
    to_agent_email = serializers.EmailField(source="to_agent.email", read_only=True)
    to_team_name = serializers.CharField(source="to_team.name", read_only=True)

    class Meta:
        model = TicketAssignmentHistory
        fields = ("id", "assigned_by_email", "to_team_name", "to_agent_email", "created_at")


class TicketSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(source="customer.email", read_only=True)
    assigned_agent_email = serializers.EmailField(source="assigned_agent.email", read_only=True)
    assigned_team_name = serializers.CharField(source="assigned_team.name", read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "customer_email",
            "assigned_team",
            "assigned_team_name",
            "assigned_agent",
            "assigned_agent_email",
            "first_response_due_at",
            "resolution_due_at",
            "first_responded_at",
            "resolved_at",
            "sla_breached",
            "ai_status",
            "ai_suggested_category",
            "ai_suggested_priority",
            "ai_summary",
            "is_master_incident",
            "parent_incident",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "status",
            "customer_email",
            "assigned_team_name",
            "assigned_agent_email",
            "first_response_due_at",
            "resolution_due_at",
            "first_responded_at",
            "resolved_at",
            "sla_breached",
            "ai_status",
            "ai_suggested_category",
            "ai_suggested_priority",
            "ai_summary",
            "created_at",
            "updated_at",
        )


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("title", "description", "category")