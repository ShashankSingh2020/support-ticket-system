from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from apps.tickets.models import Ticket, TicketReply, TicketEvent
from apps.users.models import User


class OutageClusterService:
    SIMILARITY_WINDOW_HOURS = 2

    @classmethod
    @transaction.atomic
    def evaluate_and_link_outage(cls, new_ticket: Ticket) -> bool:
        """
        Checks if the newly created ticket matches an active Master Incident
        or an ongoing surge of similar issues within the last 2 hours.
        """
        # Exclude low priority or non-infrastructure/billing outages
        if new_ticket.priority not in [Ticket.Priority.CRITICAL, Ticket.Priority.HIGH]:
            return False

        now = timezone.now()
        window_start = now - timedelta(hours=cls.SIMILARITY_WINDOW_HOURS)

        # 1. Check for an already declared Master Incident in this category
        active_master = (
            Ticket.objects.filter(
                is_master_incident=True,
                status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS],
                category=new_ticket.category,
                created_at__gte=window_start,
            )
            .order_by("-created_at")
            .first()
        )

        # 2. If no declared master, detect if 3+ similar open tickets arrived recently
        if not active_master:
            keyword_candidates = [
                word for word in new_ticket.title.lower().split()
                if len(word) > 4 and word not in ["error", "please", "failing", "server", "issue"]
            ]

            query = Q(created_at__gte=window_start) & Q(category=new_ticket.category) & ~Q(id=new_ticket.id)
            if keyword_candidates:
                keyword_q = Q()
                for word in keyword_candidates:
                    keyword_q |= Q(title__icontains=word) | Q(description__icontains=word)
                query &= keyword_q

            surge_tickets = list(Ticket.objects.filter(query)[:5])

            # If 3 or more users are experiencing this, promote the first one to Master Incident
            if len(surge_tickets) >= 2:
                active_master = surge_tickets[0]
                active_master.is_master_incident = True
                active_master.save(update_fields=["is_master_incident", "updated_at"])

        if not active_master or active_master.id == new_ticket.id:
            return False

        # 3. Link this incoming ticket as a child of the Master Incident
        new_ticket.parent_incident = active_master
        new_ticket.status = Ticket.Status.IN_PROGRESS
        new_ticket.save(update_fields=["parent_incident", "status", "updated_at"])

        # 4. Generate the automated broadcast response
        bot_user = User.objects.filter(role=User.Role.ADMIN).first()
        broadcast_msg = (
            f"Automated Notification: Our telemetry has linked this report to ongoing "
            f"Incident #{str(active_master.id)[:8]} ({active_master.title}). "
            f"Our engineering team is already actively investigating. "
            f"You will receive an update here as soon as the service is restored."
        )

        TicketReply.objects.create(
            ticket=new_ticket,
            author=bot_user,
            content=broadcast_msg,
            is_internal=False,
        )

        # Log audit trail
        TicketEvent.objects.create(
            ticket=new_ticket,
            actor=None,
            event_type=TicketEvent.EventType.STATUS_CHANGED,
            old_value="STANDALONE",
            new_value=f"LINKED_TO_{str(active_master.id)[:8]}",
            metadata={"parent_id": str(active_master.id)},
        )

        return True

    @classmethod
    @transaction.atomic
    def resolve_master_incident(cls, master_ticket: Ticket, actor: User, resolution_note: str):
        """
        Resolves the master ticket and propagates resolution + reply to all linked child tickets.
        """
        now = timezone.now()
        master_ticket.status = Ticket.Status.RESOLVED
        master_ticket.resolved_at = now
        master_ticket.save(update_fields=["status", "resolved_at", "updated_at"])

        # Find all linked child tickets
        children = master_ticket.child_tickets.filter(
            status__in=[Ticket.Status.OPEN, Ticket.Status.IN_PROGRESS]
        )

        for child in children:
            child.status = Ticket.Status.RESOLVED
            child.resolved_at = now
            child.save(update_fields=["status", "resolved_at", "updated_at"])

            # Post resolution reply to the customer
            TicketReply.objects.create(
                ticket=child,
                author=actor,
                content=f"Resolution Update: The primary incident has been resolved. {resolution_note}",
                is_internal=False,
            )