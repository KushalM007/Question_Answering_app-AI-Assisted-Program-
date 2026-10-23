"""OpenAI Responses API integration for multi-turn question answering."""

import logging
from collections.abc import Mapping, Sequence

from openai import BadRequestError, OpenAI, OpenAIError

from app.config.settings import Settings
from app.prompts.qa_prompt import SYSTEM_PROMPT


logger = logging.getLogger(__name__)


class OpenAIServiceError(Exception):
    """A safe, user-facing model-service failure."""


class OpenAIQuestionAnsweringService:
    """Generate answers using the OpenAI Responses API."""

    def __init__(self, settings: Settings, client: OpenAI | None = None) -> None:
        self._settings = settings
        try:
            self._client = (
                client if client is not None else OpenAI(api_key=settings.api_key)
            )
        except OpenAIError as error:
            logger.error(
                "OpenAI client initialization failed (%s)",
                type(error).__name__,
            )
            raise OpenAIServiceError(
                "The AI service could not be initialized. Check your configuration "
                "and try again."
            ) from None

    def generate_answer(
        self, messages: Sequence[Mapping[str, str]]
    ) -> str:
        """Return a text answer for the supplied user/assistant conversation."""
        if not messages:
            raise ValueError("At least one conversation message is required.")

        normalized_messages: list[dict[str, str]] = []
        for message in messages:
            role = message.get("role")
            content = message.get("content")
            if role not in ("user", "assistant") or not isinstance(content, str):
                raise ValueError(
                    "Conversation messages must have a valid role and text."
                )
            if not content.strip():
                raise ValueError("Conversation messages must not be empty.")
            normalized_messages.append({"role": role, "content": content})

        request_parameters = {
            "model": self._settings.model,
            "instructions": SYSTEM_PROMPT,
            "input": normalized_messages,
        }
        try:
            try:
                response = self._client.responses.create(
                    **request_parameters,
                    temperature=self._settings.temperature,
                )
            except BadRequestError as error:
                if (
                    error.param != "temperature"
                    or error.code not in ("unsupported_parameter", "unsupported_value")
                ):
                    raise
                logger.info(
                    "Model %s does not support temperature; using its default.",
                    self._settings.model,
                )
                response = self._client.responses.create(**request_parameters)
        except OpenAIError as error:
            status_code = getattr(error, "status_code", "unavailable")
            logger.error(
                "OpenAI request failed (%s, HTTP status %s)",
                type(error).__name__,
                status_code,
            )
            raise OpenAIServiceError(
                "The AI service could not complete your request. Please try again "
                "later or check your OpenAI settings."
            ) from None

        answer = response.output_text
        if not isinstance(answer, str) or not answer.strip():
            logger.warning("OpenAI returned an empty text response.")
            raise OpenAIServiceError(
                "The AI service returned an empty answer. Please try again."
            )

        logger.info("Generated an answer using model %s.", self._settings.model)
        return answer.strip()
