import pytest
from rest_framework import status
from apps.tickets.models import Ticket
from apps.tickets.services.workflow_service import TicketWorkflowService


@pytest.mark.django_db
class TestTicketWorkflowsAndPermissions:
    def test_customer_creates_ticket_and_sees_own_only(
        self, api_client, customer_user, second_customer, sla_policies
    ):
        api_client.force_authenticate(user=customer_user)
        payload = {
            "title": "Need help with login",
            "description": "Password reset email is not arriving.",
            "category": "Account",
        }
        res = api_client.post("/api/v1/tickets/", data=payload, format="json")
        assert res.status_code == status.HTTP_201_CREATED
        ticket_id = res.data["id"]

        # Customer 1 can see the ticket
        list_res = api_client.get("/api/v1/tickets/")
        assert list_res.status_code == status.HTTP_200_OK
        assert len(list_res.data) == 1
        assert list_res.data[0]["id"] == ticket_id

        # Customer 2 cannot see or access Customer 1's ticket
        api_client.force_authenticate(user=second_customer)
        c2_list = api_client.get("/api/v1/tickets/")
        assert len(c2_list.data) == 0

        c2_detail = api_client.get(f"/api/v1/tickets/{ticket_id}/")
        assert c2_detail.status_code == status.HTTP_404_NOT_FOUND

    def test_invalid_status_transition_raises_error(self, customer_user, agent_user, sla_policies):
        ticket = TicketWorkflowService.create_ticket(
            customer=customer_user,
            title="General question",
            description="How do I change my profile picture?",
        )
        assert ticket.status == Ticket.Status.OPEN

        # OPEN directly to RESOLVED is invalid according to state machine rules
        with pytest.raises(Exception):
            TicketWorkflowService.transition_status(
                ticket=ticket,
                new_status=Ticket.Status.RESOLVED,
                actor=agent_user,
            )

    def test_customer_cannot_view_internal_notes(
        self, api_client, customer_user, agent_user, sla_policies
    ):
        ticket = TicketWorkflowService.create_ticket(
            customer=customer_user,
            title="Feature request",
            description="Please add dark mode.",
        )

        # Agent posts a public reply and an internal note
        api_client.force_authenticate(user=agent_user)
        api_client.post(
            f"/api/v1/tickets/{ticket.id}/replies/",
            data={"content": "Thanks! We've added this to the roadmap.", "is_internal": False},
            format="json",
        )
        api_client.post(
            f"/api/v1/tickets/{ticket.id}/replies/",
            data={"content": "Internal: Dev team prioritized dark mode for Q4.", "is_internal": True},
            format="json",
        )

        # Customer views replies - must only see the public reply
        api_client.force_authenticate(user=customer_user)
        res = api_client.get(f"/api/v1/tickets/{ticket.id}/replies/")
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 1
        assert res.data[0]["is_internal"] is False