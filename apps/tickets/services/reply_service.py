from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.tickets.models import Ticket, TicketReply, TicketEvent
from apps.users.models import User


class TicketReplyService:
    @staticmethod
    @transaction.atomic
    def add_reply(*, ticket: Ticket, author: User, content: str, is_internal: bool = False) -> TicketReply:
        """
        Adds public reply or internal note.
        Tracks first-response timestamp when support staff post the first public reply.
        """
        if is_internal and author.role == User.Role.CUSTOMER:
            raise PermissionDenied("Customers cannot add internal notes.")

        if ticket.status == Ticket.Status.CLOSED:
            raise ValidationError("Cannot add replies to a closed ticket.")

        reply = TicketReply.objects.create(
            ticket=ticket,
            author=author,
            content=content,
            is_internal=is_internal,
        )

        # Trigger first response SLA if author is staff, reply is public, and timestamp is unset
        if (
            not is_internal
            and author.role in [User.Role.AGENT, User.Role.MANAGER, User.Role.ADMIN]
            and ticket.first_responded_at is None
        ):
            ticket.first_responded_at = timezone.now()
            ticket.save(update_fields=["first_responded_at", "updated_at"])

            TicketEvent.objects.create(
                ticket=ticket,
                actor=author,
                event_type=TicketEvent.EventType.FIRST_RESPONSE_RECORDED,
                old_value="",
                new_value=ticket.first_responded_at.isoformat(),
            )

        return reply