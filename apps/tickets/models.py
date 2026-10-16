import uuid
from django.db import models
from django.conf import settings
from apps.users.models import Team


class SLAPolicy(models.Model):
    """Configurable response targets by priority."""
    name = models.CharField(max_length=100, unique=True)
    priority = models.CharField(
        max_length=20,
        unique=True,
        help_text="Matches Ticket.Priority choices (CRITICAL, HIGH, MEDIUM, LOW)",
    )
    first_response_time_minutes = models.PositiveIntegerField(
        help_text="Required first response window in minutes"
    )
    resolution_time_minutes = models.PositiveIntegerField(
        help_text="Required resolution window in minutes"
    )

    def __str__(self):
        return f"SLA Policy: {self.priority} ({self.first_response_time_minutes}m resp / {self.resolution_time_minutes}m res)"


class Ticket(models.Model):
    class Priority(models.TextChoices):
        CRITICAL = "CRITICAL", "Critical"
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        WAITING_CUSTOMER = "WAITING_CUSTOMER", "Waiting for Customer"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"

    class AIClassificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.PositiveIntegerField(unique=True, null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets_created",
    )
    category = models.CharField(max_length=100, default="General", db_index=True)
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    assigned_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )

    # Master incident clustering & outage surge fields
    parent_incident = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_tickets",
        help_text="Points to a master incident if this ticket is part of a widespread outage surge.",
    )
    is_master_incident = models.BooleanField(
        default=False,
        help_text="Designates this ticket as the primary tracking incident for an outage surge.",
    )

    # SLA Tracking
    first_response_due_at = models.DateTimeField(null=True, blank=True)
    resolution_due_at = models.DateTimeField(null=True, blank=True)
    first_responded_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False, db_index=True)

    # AI Classification Metadata
    ai_status = models.CharField(
        max_length=20,
        choices=AIClassificationStatus.choices,
        default=AIClassificationStatus.PENDING,
        db_index=True,
    )
    ai_suggested_category = models.CharField(max_length=100, blank=True, default="")
    ai_suggested_priority = models.CharField(max_length=20, blank=True, default="")
    ai_summary = models.TextField(blank=True, default="")
    ai_confidence = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["assigned_agent", "status"]),
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["parent_incident"]),
        ]

    def __str__(self):
        return f"Ticket #{self.ticket_number or self.id}: {self.title} [{self.status}]"


class TicketReply(models.Model):
    """Public customer-agent replies or agent-only internal notes."""
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    content = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="True if this reply is a private agent/manager note.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        note_flag = "[INTERNAL] " if self.is_internal else ""
        return f"{note_flag}Reply by {self.author} on Ticket {self.ticket_id}"


class TicketAssignmentHistory(models.Model):
    """Audit trail tracking assignment handoffs."""
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="assignment_history",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="made_assignments",
    )
    from_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassigned_from",
    )
    to_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassigned_to",
    )
    from_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    to_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class TicketEvent(models.Model):
    """Immutable audit trail for ticket workflow transitions and system actions."""
    class EventType(models.TextChoices):
        CREATED = "CREATED", "Ticket Created"
        STATUS_CHANGED = "STATUS_CHANGED", "Status Changed"
        PRIORITY_CHANGED = "PRIORITY_CHANGED", "Priority Changed"
        ASSIGNMENT_CHANGED = "ASSIGNMENT_CHANGED", "Assignment Changed"
        FIRST_RESPONSE_RECORDED = "FIRST_RESPONSE", "First Response Recorded"
        RESOLVED = "RESOLVED", "Ticket Resolved"
        AI_CLASSIFICATION_SUCCESS = "AI_SUCCESS", "AI Classification Success"
        AI_CLASSIFICATION_FAILED = "AI_FAILED", "AI Classification Failed"

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="events",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="triggered_ticket_events",
    )
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
        db_index=True,
    )
    old_value = models.CharField(max_length=255, blank=True, default="")
    new_value = models.CharField(max_length=255, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} on Ticket {self.ticket_id}"