from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and optional .env."""

    app_name: str = "agentic-rag-lab"
    app_env: str = "local"
    log_level: str = "INFO"
    llm_provider: Literal["fake"] = "fake"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
