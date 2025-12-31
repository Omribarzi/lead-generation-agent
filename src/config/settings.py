"""
Application settings using pydantic-settings for environment variable management.
"""

from functools import lru_cache
from typing import Literal

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
    phantombuster_api_key: str = Field(default="", description="PhantomBuster API key")

    # Monday.com
    monday_api_key: str = Field(default="", description="Monday.com API key")
    monday_board_id: str = Field(default="5088565278", description="Monday.com board ID")

    # OpenAI
    openai_api_key: str = Field(default="", description="OpenAI API key")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")

    # Safety limits
    daily_message_limit: int = Field(default=10, ge=1, le=50, description="Max messages per day")
    daily_profile_view_limit: int = Field(default=20, ge=1, le=100, description="Max profile views per day")
    min_delay_seconds: int = Field(default=60, ge=30, description="Minimum delay between actions")
    max_delay_seconds: int = Field(default=180, ge=60, description="Maximum delay between actions")

    # Workflow settings
    require_human_approval: bool = Field(default=True, description="Require human approval for messages")
    timezone: str = Field(default="Asia/Jerusalem", description="Timezone for scheduling")

    # Working hours (Israel time)
    work_start_hour: int = Field(default=9, ge=0, le=23, description="Start of working hours")
    work_end_hour: int = Field(default=18, ge=0, le=23, description="End of working hours")

    # Calendar
    calendar_booking_link: str = Field(
        default="https://calendar.google.com/calendar/u/0/appointments/schedules/AcZssZ07bZr11Q5sapPKamtzMMuz9sgXtyBC7HYjn6XscNqMieAMNCYrnTkFbfaSYuZvGbdUroS6Zako",
        description="Google Calendar booking link",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
