from datetime import timedelta
import pytest
from django.utils import timezone
from apps.tickets.models import Ticket
from apps.tickets.services.sla_service import SLAMonitoringService
from apps.tickets.services.reply_service import TicketReplyService


@pytest.mark.django_db
class TestSLATracking:
    def test_first_response_recorded_on_agent_public_reply(
        self, customer_user, agent_user, sla_policies
    ):
        ticket = Ticket.objects.create(
            customer=customer_user,
            title="Cannot log in",
            description="My account is locked out.",
        )
        assert ticket.first_responded_at is None

        # Agent public reply sets first_responded_at
        TicketReplyService.add_reply(
            ticket=ticket,
            author=agent_user,
            content="I unlocked your account.",
            is_internal=False,
        )
        ticket.refresh_from_db()
        assert ticket.first_responded_at is not None

    def test_sla_breach_detection(self, customer_user, sla_policies):
        ticket = Ticket.objects.create(
            customer=customer_user,
            title="Overdue ticket",
            description="Nobody has answered.",
            first_response_due_at=timezone.now() - timedelta(minutes=15),
            sla_breached=False,
        )

        breached_count = SLAMonitoringService.evaluate_breaches()
        ticket.refresh_from_db()

        assert breached_count >= 1
        assert ticket.sla_breached is True