from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and optional .env."""

    app_name: str = "agentic-rag-lab"
    app_env: str = "local"
    log_level: str = "INFO"
    llm_provider: Literal["fake", "openai_compatible"] = "fake"
    embedding_provider: Literal["local_hash", "openai_compatible"] = "local_hash"
    answer_generator: Literal["local_citation", "openai_compatible"] = "local_citation"
    openai_compatible_api_key: str | None = None
    openai_compatible_base_url: str | None = None
    openai_compatible_embedding_model: str | None = None
    openai_compatible_chat_model: str | None = None
    knowledge_base_storage_path: Path = Path(".local/knowledge-bases")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
