from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.tickets.models import Ticket, TicketEvent, SLAPolicy
from apps.tickets.tasks import classify_ticket_task


VALID_STATUS_TRANSITIONS = {
    Ticket.Status.OPEN: [Ticket.Status.IN_PROGRESS, Ticket.Status.CLOSED],
    Ticket.Status.IN_PROGRESS: [
        Ticket.Status.WAITING_CUSTOMER,
        Ticket.Status.RESOLVED,
        Ticket.Status.CLOSED,
    ],
    Ticket.Status.WAITING_CUSTOMER: [Ticket.Status.IN_PROGRESS, Ticket.Status.RESOLVED],
    Ticket.Status.RESOLVED: [Ticket.Status.IN_PROGRESS, Ticket.Status.CLOSED],
    Ticket.Status.CLOSED: [],
}


class TicketWorkflowService:
    @staticmethod
    @transaction.atomic
    def create_ticket(*, customer, title, description, category="General", priority=Ticket.Priority.MEDIUM) -> Ticket:
        """
        Creates a ticket, sets SLA deadlines, logs creation audit event,
        and enqueues the Celery classification task safely after transaction commit.
        """
        now = timezone.now()
        policy = SLAPolicy.objects.filter(priority=priority).first()

        first_resp_due = now + timedelta(minutes=policy.first_response_time_minutes) if policy else now + timedelta(hours=8)
        resolution_due = now + timedelta(minutes=policy.resolution_time_minutes) if policy else now + timedelta(hours=24)

        ticket = Ticket.objects.create(
            customer=customer,
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=Ticket.Status.OPEN,
            first_response_due_at=first_resp_due,
            resolution_due_at=resolution_due,
        )

        TicketEvent.objects.create(
            ticket=ticket,
            actor=customer,
            event_type=TicketEvent.EventType.CREATED,
            old_value="",
            new_value=Ticket.Status.OPEN,
            metadata={"priority": priority, "category": category},
        )

        # Enqueue Celery task ONLY after the database transaction successfully commits
        ticket_id_str = str(ticket.id)
        transaction.on_commit(lambda: classify_ticket_task.delay(ticket_id_str))

        return ticket

    @staticmethod
    @transaction.atomic
    def transition_status(*, ticket: Ticket, new_status: str, actor) -> Ticket:
        """
        Validates state machine rules and transitions ticket status with audit logging.
        """
        if new_status == ticket.status:
            return ticket

        allowed = VALID_STATUS_TRANSITIONS.get(ticket.status, [])
        if new_status not in allowed:
            raise ValidationError(
                f"Invalid transition from {ticket.status} to {new_status}. Allowed: {allowed}"
            )

        old_status = ticket.status
        ticket.status = new_status
        now = timezone.now()

        if new_status == Ticket.Status.RESOLVED and not ticket.resolved_at:
            ticket.resolved_at = now
            TicketEvent.objects.create(
                ticket=ticket,
                actor=actor,
                event_type=TicketEvent.EventType.RESOLVED,
                old_value=old_status,
                new_value=new_status,
            )

        ticket.save(update_fields=["status", "resolved_at", "updated_at"])

        TicketEvent.objects.create(
            ticket=ticket,
            actor=actor,
            event_type=TicketEvent.EventType.STATUS_CHANGED,
            old_value=old_status,
            new_value=new_status,
        )
        return ticket