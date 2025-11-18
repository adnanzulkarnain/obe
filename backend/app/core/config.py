"""
Application Configuration Module

This module manages all application settings using Pydantic's BaseSettings.
Following Clean Code principles: Single Responsibility, Type Safety, and Clear naming.
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """
    Database configuration settings.

    Separated from main settings following Single Responsibility Principle.
    """

    host: str = Field(default="localhost", description="Database host address")
    port: int = Field(default=5432, description="Database port number")
    name: str = Field(default="obe_system", description="Database name")
    user: str = Field(default="obe_user", description="Database user")
    password: str = Field(default="", description="Database password")

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    def get_connection_url(self) -> str:
        """
        Generate PostgreSQL connection URL.

        Returns:
            str: SQLAlchemy-compatible database URL
        """
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class SecuritySettings(BaseSettings):
    """
    Security and authentication configuration.

    Manages JWT tokens and encryption settings.
    """

    secret_key: str = Field(
        ...,
        description="Secret key for JWT encoding (MUST be changed in production)"
    )
    algorithm: str = Field(default="HS256", description="JWT encoding algorithm")
    access_token_expire_minutes: int = Field(
        default=120,
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @validator("secret_key")
    def validate_secret_key(cls, value: str) -> str:
        """Ensure secret key has minimum length for security."""
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return value


class CORSSettings(BaseSettings):
    """
    CORS (Cross-Origin Resource Sharing) configuration.

    Controls which origins can access the API.
    """

    origins: List[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins"
    )
    allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    allow_methods: List[str] = Field(
        default=["*"],
        description="Allowed HTTP methods"
    )
    allow_headers: List[str] = Field(
        default=["*"],
        description="Allowed HTTP headers"
    )

    model_config = SettingsConfigDict(
        env_prefix="BACKEND_CORS_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )


class ApplicationSettings(BaseSettings):
    """
    Main application settings.

    Aggregates all configuration sub-modules.
    Following Composition over Inheritance principle.
    """

    # Application Info
    app_name: str = Field(default="OBE System API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: str = Field(
        default="production",
        description="Environment: development, staging, production"
    )

    # API Configuration
    api_v1_prefix: str = Field(
        default="/api/v1",
        description="API version 1 URL prefix"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    # Composed settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)

    def is_development(self) -> bool:
        """Check if application is running in development mode."""
        return self.environment.lower() == "development"

    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> ApplicationSettings:
    """
    Get application settings instance.

    Uses LRU cache to ensure singleton pattern - settings are loaded once.
    This is a Clean Code practice for expensive operations.

    Returns:
        ApplicationSettings: Cached settings instance
    """
    return ApplicationSettings()


# Convenience exports
settings = get_settings()
