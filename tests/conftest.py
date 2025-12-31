"""
Pytest configuration and shared fixtures.
"""

import pytest


@pytest.fixture
def mock_settings(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("PHANTOMBUSTER_API_KEY", "test_phantom_key")
    monkeypatch.setenv("MONDAY_API_KEY", "test_monday_key")
    monkeypatch.setenv("MONDAY_BOARD_ID", "12345")
    monkeypatch.setenv("OPENAI_API_KEY", "test_openai_key")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DAILY_MESSAGE_LIMIT", "10")
    monkeypatch.setenv("REQUIRE_HUMAN_APPROVAL", "true")
    monkeypatch.setenv("TIMEZONE", "Asia/Jerusalem")
