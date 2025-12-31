"""Tests for configuration settings."""
import os
import pytest


class TestSettings:
    """Test settings configuration."""

    def test_settings_import(self):
        """Test that settings module can be imported."""
        from src.config.settings import Settings
        assert Settings is not None

    def test_get_settings_function_exists(self):
        """Test that get_settings function exists."""
        from src.config.settings import get_settings
        assert callable(get_settings)

    def test_default_values(self):
        """Test default configuration values."""
        from src.config.settings import Settings

        # Create settings with minimal required values
        settings = Settings(
            PHANTOMBUSTER_API_KEY="test_key",
            MONDAY_API_KEY="test_key",
            OPENAI_API_KEY="test_key"
        )

        assert settings.DAILY_MESSAGE_LIMIT == 10
        assert settings.REQUIRE_HUMAN_APPROVAL == True
        assert settings.TIMEZONE == "Asia/Jerusalem"
        assert settings.MONDAY_BOARD_ID == "5088565278"

    def test_redis_url_default(self):
        """Test Redis URL has correct default."""
        from src.config.settings import Settings

        settings = Settings(
            PHANTOMBUSTER_API_KEY="test_key",
            MONDAY_API_KEY="test_key",
            OPENAI_API_KEY="test_key"
        )

        assert settings.REDIS_URL == "redis://localhost:6379/0"

    def test_env_file_example_exists(self):
        """Test that .env.example file exists."""
        assert os.path.exists(".env.example"), ".env.example file is missing"

    def test_env_example_has_required_keys(self):
        """Test that .env.example contains all required keys."""
        with open(".env.example", "r") as f:
            content = f.read()

        required_keys = [
            "PHANTOMBUSTER_API_KEY",
            "MONDAY_API_KEY",
            "OPENAI_API_KEY",
            "REDIS_URL",
            "DAILY_MESSAGE_LIMIT",
            "MONDAY_BOARD_ID"
        ]

        for key in required_keys:
            assert key in content, f"Missing {key} in .env.example"
