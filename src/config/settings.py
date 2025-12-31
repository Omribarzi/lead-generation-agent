"""
Application settings using pydantic-settings for environment variable management.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # PhantomBuster
    PHANTOMBUSTER_API_KEY: str = Field(default="", description="PhantomBuster API key")

    # Monday.com
    MONDAY_API_KEY: str = Field(default="", description="Monday.com API key")
    MONDAY_BOARD_ID: str = Field(default="5088565278", description="Monday.com board ID")

    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Safety limits
    DAILY_MESSAGE_LIMIT: int = Field(default=10, ge=1, le=50, description="Max messages per day")
    DAILY_PROFILE_VIEW_LIMIT: int = Field(default=20, ge=1, le=100, description="Max profile views per day")
    MIN_DELAY_SECONDS: int = Field(default=60, ge=30, description="Minimum delay between actions")
    MAX_DELAY_SECONDS: int = Field(default=180, ge=60, description="Maximum delay between actions")

    # Workflow settings
    REQUIRE_HUMAN_APPROVAL: bool = Field(default=True, description="Require human approval for messages")
    TIMEZONE: str = Field(default="Asia/Jerusalem", description="Timezone for scheduling")

    # Working hours (Israel time)
    WORK_START_HOUR: int = Field(default=9, ge=0, le=23, description="Start of working hours")
    WORK_END_HOUR: int = Field(default=18, ge=0, le=23, description="End of working hours")

    # Calendar
    CALENDAR_BOOKING_LINK: str = Field(
        default="https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ07bZr11Q5sapPKamtzMMuz9sgXtyBC7HYjn6XscNqMieAMNCYrnTkFbfaSYuZvGbdUroS6Zako",
        description="Google Calendar booking link",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
