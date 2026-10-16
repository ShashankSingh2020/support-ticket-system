from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from apps.tickets.models import Ticket, TicketEvent


class SLAMonitoringService:
    @classmethod
    @transaction.atomic
    def evaluate_breaches(cls) -> int:
        """
        Idempotently scans active tickets and flags SLA breaches for:
        1. First response deadline exceeded before any staff reply.
        2. Resolution deadline exceeded while ticket is still unresolved.
        Returns the count of newly flagged tickets.
        """
        now = timezone.now()

        # Find unbreached tickets where first response or resolution is overdue
        first_resp_overdue = Q(
            first_responded_at__isnull=True,
            first_response_due_at__lt=now,
        )
        resolution_overdue = Q(
            status__in=[
                Ticket.Status.OPEN,
                Ticket.Status.IN_PROGRESS,
                Ticket.Status.WAITING_CUSTOMER,
            ],
            resolution_due_at__lt=now,
        )

        overdue_tickets = (
            Ticket.objects.select_for_update()
            .filter(sla_breached=False)
            .filter(first_resp_overdue | resolution_overdue)
        )

        breached_count = 0
        for ticket in overdue_tickets:
            ticket.sla_breached = True
            ticket.save(update_fields=["sla_breached", "updated_at"])

            reason = "First response overdue" if (ticket.first_response_due_at and ticket.first_response_due_at < now and not ticket.first_responded_at) else "Resolution overdue"
            TicketEvent.objects.create(
                ticket=ticket,
                actor=None,
                event_type=TicketEvent.EventType.STATUS_CHANGED,
                old_value="SLA_MET",
                new_value="SLA_BREACHED",
                metadata={"reason": reason, "evaluated_at": now.isoformat()},
            )
            breached_count += 1

        return breached_count