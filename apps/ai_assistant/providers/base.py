from abc import ABC, abstractmethod
from apps.ai_assistant.schema import ClassificationResult


class BaseAIProvider(ABC):
    """Abstract interface defining required AI classification capabilities."""

    @abstractmethod
    def classify_ticket(self, title: str, description: str) -> ClassificationResult:
        """Analyze title and description and return validated ClassificationResult."""
        pass