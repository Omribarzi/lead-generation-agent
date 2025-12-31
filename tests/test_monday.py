"""Tests for Monday.com integration."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestMondayClient:
    """Test Monday.com client."""

    def test_import_monday_client(self):
        """Test that MondayClient can be imported."""
        from src.integrations.monday_client import MondayClient
        assert MondayClient is not None

    def test_client_initialization(self):
        """Test client initializes with settings."""
        with patch.dict('os.environ', {
            'MONDAY_API_KEY': 'test_key',
            'MONDAY_BOARD_ID': '12345',
            'PHANTOMBUSTER_API_KEY': 'test',
            'OPENAI_API_KEY': 'test'
        }):
            # Clear the settings cache
            from src.config.settings import get_settings
            get_settings.cache_clear()

            from src.integrations.monday_client import MondayClient
            client = MondayClient()
            assert client is not None

    def test_lead_dataclass_exists(self):
        """Test Lead dataclass exists with required fields."""
        from src.integrations.monday_client import Lead

        lead = Lead(
            first_name="Test",
            last_name="User",
            company="Test Company",
            position="CSR Manager",
            linkedin_url="https://linkedin.com/in/test"
        )

        assert lead.first_name == "Test"
        assert lead.last_name == "User"
        assert lead.full_name == "Test User"
        assert lead.company == "Test Company"
        assert lead.position == "CSR Manager"
        assert lead.linkedin_url == "https://linkedin.com/in/test"
        assert lead.status == "New"  # Default value

    @pytest.mark.asyncio
    async def test_create_lead_method_exists(self):
        """Test create_lead method exists."""
        with patch.dict('os.environ', {
            'MONDAY_API_KEY': 'test_key',
            'MONDAY_BOARD_ID': '12345',
            'PHANTOMBUSTER_API_KEY': 'test',
            'OPENAI_API_KEY': 'test'
        }):
            from src.config.settings import get_settings
            get_settings.cache_clear()

            from src.integrations.monday_client import MondayClient
            client = MondayClient()
            assert hasattr(client, 'create_lead')
            assert callable(client.create_lead)

    @pytest.mark.asyncio
    async def test_update_lead_status_method_exists(self):
        """Test update_lead_status method exists."""
        with patch.dict('os.environ', {
            'MONDAY_API_KEY': 'test_key',
            'MONDAY_BOARD_ID': '12345',
            'PHANTOMBUSTER_API_KEY': 'test',
            'OPENAI_API_KEY': 'test'
        }):
            from src.config.settings import get_settings
            get_settings.cache_clear()

            from src.integrations.monday_client import MondayClient
            client = MondayClient()
            assert hasattr(client, 'update_lead_status')

    @pytest.mark.asyncio
    async def test_get_leads_by_status_method_exists(self):
        """Test get_leads_by_status method exists."""
        with patch.dict('os.environ', {
            'MONDAY_API_KEY': 'test_key',
            'MONDAY_BOARD_ID': '12345',
            'PHANTOMBUSTER_API_KEY': 'test',
            'OPENAI_API_KEY': 'test'
        }):
            from src.config.settings import get_settings
            get_settings.cache_clear()

            from src.integrations.monday_client import MondayClient
            client = MondayClient()
            assert hasattr(client, 'get_leads_by_status')

    @pytest.mark.asyncio
    async def test_append_to_conversation_log_method_exists(self):
        """Test append_to_conversation_log method exists."""
        with patch.dict('os.environ', {
            'MONDAY_API_KEY': 'test_key',
            'MONDAY_BOARD_ID': '12345',
            'PHANTOMBUSTER_API_KEY': 'test',
            'OPENAI_API_KEY': 'test'
        }):
            from src.config.settings import get_settings
            get_settings.cache_clear()

            from src.integrations.monday_client import MondayClient
            client = MondayClient()
            assert hasattr(client, 'append_to_conversation_log')

    @pytest.mark.asyncio
    async def test_create_lead_mocked(self):
        """Test create_lead with mocked API."""
        with patch.dict('os.environ', {
            'MONDAY_API_KEY': 'test_key',
            'MONDAY_BOARD_ID': '12345',
            'PHANTOMBUSTER_API_KEY': 'test',
            'OPENAI_API_KEY': 'test'
        }):
            from src.config.settings import get_settings
            get_settings.cache_clear()

            from src.integrations.monday_client import MondayClient, Lead

            client = MondayClient()

            # Mock the API call
            mock_response = {"data": {"create_item": {"id": "123456"}}}
            client._execute_query = AsyncMock(return_value=mock_response)

            lead = Lead(
                first_name="Test",
                last_name="User",
                company="Test Company",
                position="CSR Manager",
                linkedin_url="https://linkedin.com/in/test"
            )

            result = await client.create_lead(lead)
            assert result == "123456"


class TestLeadStatus:
    """Test lead status constants."""

    def test_lead_status_constants_exist(self):
        """Test that LEAD_STATUS constants are defined."""
        from src.integrations.monday_client import LEAD_STATUS

        assert "NEW" in LEAD_STATUS
        assert "CONTACTED" in LEAD_STATUS
        assert "IN_CONVERSATION" in LEAD_STATUS
        assert "MEETING_SCHEDULED" in LEAD_STATUS
        assert "NOT_INTERESTED" in LEAD_STATUS
