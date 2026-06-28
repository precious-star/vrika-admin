"""Vrika Admin backend configuration."""

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongodb_uri: str = "mongodb://admin-mongo:27017"
    mongodb_db: str = "vrika_admin"

    jwt_secret: str = "change-me-generate-with-openssl-rand-hex-32"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

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
    cors_origins: list[str] = ["http://localhost:4001"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
