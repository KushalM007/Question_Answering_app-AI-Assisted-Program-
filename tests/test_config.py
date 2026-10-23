"""Tests for environment-based configuration."""

import pytest

from app.config import settings
from app.config.settings import ConfigurationError, get_settings


@pytest.fixture(autouse=True)
def isolate_dotenv_loading(monkeypatch):
    monkeypatch.setattr(settings, "load_dotenv", lambda **_kwargs: False)


def test_loads_configured_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("TEMPERATURE", "0.7")

    config = get_settings()

    assert config.api_key == "test-key-not-a-real-secret"
    assert config.model == "test-model"
    assert config.temperature == 0.7
    assert "test-key-not-a-real-secret" not in repr(config)


def test_uses_defaults_for_optional_values(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("TEMPERATURE", raising=False)

    config = get_settings()

    assert config.model == settings.DEFAULT_MODEL
    assert config.temperature == settings.DEFAULT_TEMPERATURE


def test_missing_api_key_fails_clearly(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ConfigurationError, match="API key is not configured"):
        get_settings()


def test_example_placeholder_is_not_accepted_as_api_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "your_openai_api_key_here")

    with pytest.raises(ConfigurationError, match="question_answering_app/.env"):
        get_settings()


@pytest.mark.parametrize("value", ["not-a-number", "nan", "inf", "-0.1", "2.1"])
def test_invalid_temperature_fails(monkeypatch, value):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("TEMPERATURE", value)

    with pytest.raises(ConfigurationError, match="TEMPERATURE"):
        get_settings()
