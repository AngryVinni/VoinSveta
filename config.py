"""Configuration loading for Telegram/OpenAI tokens."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def read_token_from_file(path: str) -> str | None:
    """Read a token from a local text file.

    Returns:
        Token string if file exists and is not empty, otherwise None.
    """
    token_path = Path(path)
    if not token_path.exists():
        return None

    token = token_path.read_text(encoding="utf-8").strip()
    if not token:
        return None
    return token


class Settings(BaseSettings):
    """Application settings loaded from environment and optional token file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_token: str | None = Field(default=None, alias="TELEGRAM_TOKEN")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")


def load_settings() -> Settings:
    """Load settings from env and token files.

    Resolution order:
    - TELEGRAM_TOKEN from env/.env
    - telegram-token.txt
    - openai-token.txt (legacy fallback only for OpenAI key)
    """
    settings = Settings()

    if not settings.telegram_token:
        settings.telegram_token = read_token_from_file("telegram-token.txt")

    if not settings.telegram_token:
        raise RuntimeError(
            "Telegram token is missing. Set TELEGRAM_TOKEN in .env or create telegram-token.txt"
        )

    if not settings.openai_api_key:
        settings.openai_api_key = read_token_from_file("openai-token.txt")

    if not settings.openai_api_key:
        raise RuntimeError(
            "OpenAI key is missing. Set OPENAI_API_KEY in .env or create openai-token.txt"
        )

    return settings
