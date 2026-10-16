import json
import logging
from django.conf import settings
from apps.ai_assistant.providers.base import BaseAIProvider
from apps.ai_assistant.schema import ClassificationResult
from apps.ai_assistant.providers.mock_provider import MockAIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini LLM provider using structured JSON output.
    Falls back cleanly to MockAIProvider if the key is missing or calls fail.
    """

    def __init__(self):
        self.api_key = getattr(settings, "GEMINI_API_KEY", "")
        self.fallback = MockAIProvider()

    def classify_ticket(self, title: str, description: str) -> ClassificationResult:
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured; using deterministic MockAIProvider fallback.")
            return self.fallback.classify_ticket(title, description)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            prompt = (
                f"You are a technical support ticket triage engine.\n"
                f"Classify the following ticket:\n"
                f"Title: {title}\n"
                f"Description: {description}\n\n"
                f"Respond ONLY with valid JSON with these exact keys:\n"
                f'{{"category": "Infrastructure|Billing|Technical|General", '
                f'"priority": "CRITICAL|HIGH|MEDIUM|LOW", '
                f'"summary": string, "confidence": float, "suggested_reply": string}}'
            )

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            raw_text = response.text
            parsed = json.loads(raw_text)
            return ClassificationResult.validate_and_sanitize(parsed)

        except Exception as exc:
            logger.error("Gemini classification failed: %s. Using mock fallback.", str(exc))
            return self.fallback.classify_ticket(title, description)