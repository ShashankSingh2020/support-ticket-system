from dataclasses import dataclass
from typing import Optional
from apps.tickets.models import Ticket


@dataclass
class ClassificationResult:
    category: str
    priority: str
    summary: str
    confidence: float
    suggested_reply: Optional[str] = None

    @classmethod
    def validate_and_sanitize(cls, raw: dict) -> "ClassificationResult":
        """
        Validates raw dictionary output from any AI provider against strict constraints.
        Enforces allowed priorities and non-empty summaries.
        """
        valid_priorities = {p.value for p in Ticket.Priority}
        priority = str(raw.get("priority", "")).upper()
        if priority not in valid_priorities:
            priority = Ticket.Priority.MEDIUM

        category = str(raw.get("category", "General")).strip() or "General"
        summary = str(raw.get("summary", "")).strip()
        if not summary:
            summary = "Summary unavailable."

        try:
            confidence = float(raw.get("confidence", 0.0))
            confidence = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            confidence = 0.5

        suggested_reply = raw.get("suggested_reply")
        if suggested_reply is not None:
            suggested_reply = str(suggested_reply).strip()

        return cls(
            category=category,
            priority=priority,
            summary=summary,
            confidence=confidence,
            suggested_reply=suggested_reply,
        )