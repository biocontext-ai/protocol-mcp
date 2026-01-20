"""Configuration settings for protocol-mcp."""

import os
from functools import lru_cache

from pydantic import BaseModel, SecretStr


class ProtocolsIOConfig(BaseModel):
    """Configuration for protocols.io API client."""

    base_url_v3: str = "https://www.protocols.io/api/v3"
    base_url_v4: str = "https://www.protocols.io/api/v4"
    access_token: SecretStr | None = None


class Settings(BaseModel):
    """Application settings."""

    protocols_io: ProtocolsIOConfig


@lru_cache
def get_settings() -> Settings:
    """Load settings from environment variables.

    Returns
    -------
    Settings
        Application settings loaded from environment.
    """
    access_token = os.environ.get("PROTOCOLS_IO_ACCESS_TOKEN")

    return Settings(
        protocols_io=ProtocolsIOConfig(
            access_token=SecretStr(access_token) if access_token else None,
        )
    )
