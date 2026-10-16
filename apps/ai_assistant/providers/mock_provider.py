import re
from apps.ai_assistant.providers.base import BaseAIProvider
from apps.ai_assistant.schema import ClassificationResult
from apps.tickets.models import Ticket


class MockAIProvider(BaseAIProvider):
    """
    Deterministic rule-based mock provider.
    Runs locally with zero external network dependencies or API keys.
    """

    def classify_ticket(self, title: str, description: str) -> ClassificationResult:
        combined = f"{title} {description}".lower()

        # Keyword mapping rules
        if any(w in combined for w in ["urgent", "down", "outage", "security breach", "data leak"]):
            category = "Infrastructure"
            priority = Ticket.Priority.CRITICAL
            confidence = 0.98
            suggested_reply = "We have escalated this critical outage to our primary infrastructure on-call engineer."
        elif any(w in combined for w in ["charge", "billing", "invoice", "payment", "refund", "subscription"]):
            category = "Billing"
            priority = Ticket.Priority.HIGH
            confidence = 0.92
            suggested_reply = "Thank you for reaching out to Billing. Our finance specialists are reviewing the charge history."
        elif any(w in combined for w in ["bug", "error", "exception", "failed", "crash"]):
            category = "Technical"
            priority = Ticket.Priority.MEDIUM
            confidence = 0.85
            suggested_reply = "Our technical team has registered this incident and is inspecting application logs."
        else:
            category = "General"
            priority = Ticket.Priority.LOW
            confidence = 0.70
            suggested_reply = "Thank you for contacting support. An agent will respond shortly."

        clean_summary = re.sub(r"\s+", " ", title.strip())[:150]

        return ClassificationResult(
            category=category,
            priority=priority,
            summary=f"Automated synopsis: {clean_summary}",
            confidence=confidence,
            suggested_reply=suggested_reply,
        )