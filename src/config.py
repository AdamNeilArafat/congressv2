"""Configuration management for the campaign pipeline."""
from functools import lru_cache
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    fec_api_key: str = ""
    congress_api_key: str = ""
    db_url: str = "sqlite:///campaign.db"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()

