"""Unit tests for the OpenAI service using mocked SDK responses."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from openai import APIError, BadRequestError

from app.config.settings import Settings
from app.services.openai_service import (
    OpenAIQuestionAnsweringService,
    OpenAIServiceError,
)


@pytest.fixture
def settings():
    return Settings(
        api_key="test-key-not-a-real-secret",
        model="test-model",
        temperature=0.4,
    )


def test_initializes_openai_client(settings, monkeypatch):
    client = MagicMock()
    openai_constructor = MagicMock(return_value=client)
    monkeypatch.setattr("app.services.openai_service.OpenAI", openai_constructor)

    service = OpenAIQuestionAnsweringService(settings)

    openai_constructor.assert_called_once_with(api_key=settings.api_key)
    assert service._client is client


def test_returns_response_text_and_uses_conversation(settings):
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(
        output_text="A concise answer."
    )
    service = OpenAIQuestionAnsweringService(settings, client=client)
    messages = [
        {"role": "user", "content": "What is photosynthesis?"},
        {"role": "assistant", "content": "It is how plants make food."},
        {"role": "user", "content": "Where does it happen?"},
    ]

    answer = service.generate_answer(messages)

    assert answer == "A concise answer."
    client.responses.create.assert_called_once()
    call = client.responses.create.call_args.kwargs
    assert call["model"] == "test-model"
    assert call["temperature"] == 0.4
    assert call["input"] == messages
    assert "conversation history" in call["instructions"]


def test_api_failure_is_sanitized(settings):
    client = MagicMock()
    client.responses.create.side_effect = APIError(
        "private error containing test-key-not-a-real-secret",
        request=None,
        body=None,
    )
    service = OpenAIQuestionAnsweringService(settings, client=client)

    with pytest.raises(OpenAIServiceError) as error:
        service.generate_answer([{"role": "user", "content": "Hello"}])

    assert "test-key-not-a-real-secret" not in str(error.value)
    assert "private error" not in str(error.value)


def test_empty_model_response_is_reported(settings):
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(output_text=" ")
    service = OpenAIQuestionAnsweringService(settings, client=client)

    with pytest.raises(OpenAIServiceError, match="empty answer"):
        service.generate_answer([{"role": "user", "content": "Hello"}])


def test_retries_without_temperature_when_model_rejects_it(settings):
    client = MagicMock()
    response = SimpleNamespace(output_text="Answer from model default.")
    temperature_error = BadRequestError(
        "temperature is unsupported",
        response=SimpleNamespace(
            request=object(),
            status_code=400,
            headers={},
        ),
        body={
            "message": "temperature is unsupported",
            "param": "temperature",
            "code": "unsupported_parameter",
        },
    )
    client.responses.create.side_effect = [temperature_error, response]
    service = OpenAIQuestionAnsweringService(settings, client=client)

    answer = service.generate_answer([{"role": "user", "content": "Hello"}])

    assert answer == "Answer from model default."
    assert client.responses.create.call_count == 2
    assert "temperature" in client.responses.create.call_args_list[0].kwargs
    assert "temperature" not in client.responses.create.call_args_list[1].kwargs


def test_empty_conversation_does_not_call_api(settings):
    client = MagicMock()
    service = OpenAIQuestionAnsweringService(settings, client=client)

    with pytest.raises(ValueError, match="At least one"):
        service.generate_answer([])

    client.responses.create.assert_not_called()
