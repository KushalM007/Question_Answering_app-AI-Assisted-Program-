"""Load and validate application settings from environment variables."""

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.2


class ConfigurationError(Exception):
    """Raised when required or invalid application configuration is found."""


@dataclass(frozen=True)
class Settings:
    """Validated runtime configuration; the API key is excluded from repr."""

    api_key: str = field(repr=False)
    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE


def get_settings() -> Settings:
    """Load .env values and return validated settings without exposing secrets."""
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ConfigurationError(
            "The Gemini API key is not configured. Open "
            "question_answering_app/.env and set GEMINI_API_KEY to your own key."
        )

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise ConfigurationError("GEMINI_MODEL must not be empty.")

    raw_temperature = os.getenv("TEMPERATURE", str(DEFAULT_TEMPERATURE)).strip()
    try:
        temperature = float(raw_temperature)
    except ValueError as error:
        raise ConfigurationError(
            "TEMPERATURE must be a number between 0 and 2."
        ) from error

    if not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise ConfigurationError("TEMPERATURE must be a number between 0 and 2.")

    return Settings(api_key=api_key, model=model, temperature=temperature)
