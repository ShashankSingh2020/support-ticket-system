import pytest
from apps.tickets.models import Ticket
from apps.ai_assistant.service import TicketClassificationService
from apps.ai_assistant.schema import ClassificationResult


@pytest.mark.django_db
class TestAIAssistant:
    def test_mock_classification_critical_outage(self, customer_user, sla_policies):
        ticket = Ticket.objects.create(
            customer=customer_user,
            title="Major outage in Europe zone",
            description="Our service is completely down and failing.",
        )

        result = TicketClassificationService.classify_and_apply(str(ticket.id))
        ticket.refresh_from_db()

        assert result.priority == Ticket.Priority.CRITICAL
        assert result.category == "Infrastructure"
        assert ticket.ai_status == Ticket.AIClassificationStatus.COMPLETED
        assert ticket.ai_suggested_priority == Ticket.Priority.CRITICAL

    def test_schema_sanitization_fallback(self):
        malformed_raw = {
            "category": "",
            "priority": "NON_EXISTENT_PRIORITY",
            "summary": "",
            "confidence": "invalid_number",
        }
        sanitized = ClassificationResult.validate_and_sanitize(malformed_raw)

        assert sanitized.priority == Ticket.Priority.MEDIUM
        assert sanitized.category == "General"
        assert sanitized.summary == "Summary unavailable."
        assert sanitized.confidence == 0.5