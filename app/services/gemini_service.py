"""Google Gemini API integration for multi-turn question answering."""

import logging
from collections.abc import Mapping, Sequence

from google import genai
from google.genai import errors, types

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """A safe, user-facing model-service failure."""


class GeminiQuestionAnsweringService:
    """Generate answers using the Google Gen AI SDK."""

    def __init__(self, settings: Settings, client=None) -> None:
        self._settings = settings
        try:
            self._client = client if client is not None else genai.Client(api_key=settings.api_key)
        except Exception as error:
            logger.error("Gemini client initialization failed (%s)", type(error).__name__)
            raise GeminiServiceError(
                "The Gemini service could not be initialized. Check your API key and configuration."
            ) from None

    def generate_answer(self, messages: Sequence[Mapping[str, str]]) -> str:
        """Return a text answer for the supplied user/assistant conversation."""
        if not messages:
            raise ValueError("At least one conversation message is required.")

        contents = []
        for message in messages:
            role = message.get("role")
            content = message.get("content")
            if role not in ("user", "assistant") or not isinstance(content, str):
                raise ValueError("Conversation messages must have a valid role and text.")
            if not content.strip():
                raise ValueError("Conversation messages must not be empty.")
            # Gemini uses 'model' for assistant turns.
            contents.append(
                types.Content(
                    role="model" if role == "assistant" else "user",
                    parts=[types.Part.from_text(text=content)],
                )
            )

        try:
            response = self._client.models.generate_content(
                model=self._settings.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=self._settings.temperature,
                ),
            )
        except errors.APIError as error:
            logger.error(
                "Gemini request failed (%s, HTTP status %s)",
                type(error).__name__,
                getattr(error, "code", "unavailable"),
            )
            raise GeminiServiceError(
                "Gemini could not complete your request. Check that your API key is valid, "
                "the selected model is available, and your quota has not been exceeded."
            ) from None
        except Exception as error:
            logger.error("Unexpected Gemini request failure (%s)", type(error).__name__)
            raise GeminiServiceError(
                "An unexpected error occurred while contacting Gemini. Please try again."
            ) from None

        answer = response.text
        if not isinstance(answer, str) or not answer.strip():
            logger.warning("Gemini returned an empty text response.")
            raise GeminiServiceError("Gemini returned an empty answer. Please try again.")

        logger.info("Generated an answer using Gemini model %s.", self._settings.model)
        return answer.strip()
