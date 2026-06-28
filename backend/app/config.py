"""Vrika Admin backend configuration."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://127.0.0.1:27017"
    mongodb_db: str = "cipherstrike"

    redis_url: str = "redis://127.0.0.1:6379/0"

    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    # Agent microservice URL (for fetching tool catalog)
    agent_microservice_url: str = Field(
        default="http://127.0.0.1:8888",
        validation_alias=AliasChoices("AGENT_MICROSERVICE_URL"),
    )
    agent_base_url: str = Field(
        default="http://127.0.0.1:8888",
        validation_alias=AliasChoices("AGENT_BASE_URL", "AGENT_MICROSERVICE_URL"),
    )
    agent_api_token: str = Field(
        default="",
        validation_alias=AliasChoices("AGENT_API_TOKEN"),
    )
    cipherstrike_bridge_secret: str = Field(
        default="",
        validation_alias=AliasChoices("CIPHERSTRIKE_BRIDGE_SECRET"),
    )
    agent_timeout_seconds: float = Field(default=30.0)

    # License signing keys (ECDSA P-256)
    license_private_key_path: str = Field(
        default="/app/keys/license_private.pem",
        validation_alias=AliasChoices("LICENSE_PRIVATE_KEY_PATH"),
    )
    license_public_key_path: str = Field(
        default="/app/keys/license_public.pem",
        validation_alias=AliasChoices("LICENSE_PUBLIC_KEY_PATH"),
    )

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
