from django.conf import settings
from django.db import transaction
from apps.tickets.models import Ticket, TicketEvent
from apps.ai_assistant.providers.mock_provider import MockAIProvider
from apps.ai_assistant.providers.gemini_provider import GeminiProvider
from apps.ai_assistant.schema import ClassificationResult


class TicketClassificationService:
    @staticmethod
    def get_provider():
        provider_name = getattr(settings, "AI_PROVIDER", "mock").lower()
        if provider_name == "gemini":
            return GeminiProvider()
        return MockAIProvider()

    @classmethod
    @transaction.atomic
    def classify_and_apply(cls, ticket_id: str) -> ClassificationResult:
        """
        Runs classification and writes validated results to the Ticket and audit trail.
        Safe against provider failure.
        """
        ticket = Ticket.objects.select_for_update().get(id=ticket_id)
        provider = cls.get_provider()

        try:
            result = provider.classify_ticket(ticket.title, ticket.description)

            ticket.ai_suggested_category = result.category
            ticket.ai_suggested_priority = result.priority
            ticket.ai_summary = result.summary
            ticket.ai_confidence = result.confidence
            ticket.ai_status = Ticket.AIClassificationStatus.COMPLETED
            ticket.save(update_fields=[
                "ai_suggested_category",
                "ai_suggested_priority",
                "ai_summary",
                "ai_confidence",
                "ai_status",
                "updated_at",
            ])

            TicketEvent.objects.create(
                ticket=ticket,
                actor=None,
                event_type=TicketEvent.EventType.AI_CLASSIFICATION_SUCCESS,
                old_value="",
                new_value=result.priority,
                metadata={
                    "category": result.category,
                    "confidence": result.confidence,
                    "summary": result.summary,
                },
            )
            return result

        except Exception as exc:
            ticket.ai_status = Ticket.AIClassificationStatus.FAILED
            ticket.save(update_fields=["ai_status", "updated_at"])

            TicketEvent.objects.create(
                ticket=ticket,
                actor=None,
                event_type=TicketEvent.EventType.AI_CLASSIFICATION_FAILED,
                old_value="",
                new_value="FAILED",
                metadata={"error": str(exc)},
            )
            raise exc