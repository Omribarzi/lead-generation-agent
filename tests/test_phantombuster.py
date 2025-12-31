"""Tests for PhantomBuster integration."""
import pytest
from unittest.mock import AsyncMock, patch


class TestPhantomBusterClient:
    """Test PhantomBuster client."""

    def test_import_phantombuster_client(self):
        """Test that PhantomBusterClient can be imported."""
        from src.integrations.phantombuster import PhantomBusterClient

        assert PhantomBusterClient is not None

    def test_client_initialization(self):
        """Test client initializes with settings."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import PhantomBusterClient

            client = PhantomBusterClient()
            assert client is not None
            assert client.api_key == "test_key"

    def test_linkedin_profile_dataclass(self):
        """Test LinkedInProfile dataclass."""
        from src.integrations.phantombuster import LinkedInProfile

        profile = LinkedInProfile(
            linkedin_url="https://linkedin.com/in/johndoe",
            first_name="John",
            last_name="Doe",
            company="Test Corp",
            position="CSR Manager",
        )

        assert profile.linkedin_url == "https://linkedin.com/in/johndoe"
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.full_name == "John Doe"
        assert profile.company == "Test Corp"
        assert profile.position == "CSR Manager"

    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        from src.integrations.phantombuster import AgentStatus

        assert AgentStatus.RUNNING == "running"
        assert AgentStatus.FINISHED == "finished"
        assert AgentStatus.ERROR == "error"
        assert AgentStatus.LAUNCHING == "launching"

    def test_agent_output_dataclass(self):
        """Test AgentOutput dataclass."""
        from src.integrations.phantombuster import AgentOutput, AgentStatus

        output = AgentOutput(
            container_id="container123",
            status=AgentStatus.FINISHED,
            result_object={"key": "value"},
            output="test output",
            exit_code=0,
        )

        assert output.container_id == "container123"
        assert output.status == AgentStatus.FINISHED
        assert output.result_object == {"key": "value"}
        assert output.output == "test output"
        assert output.exit_code == 0

    @pytest.mark.asyncio
    async def test_launch_agent_method_exists(self):
        """Test launch_agent method exists."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import PhantomBusterClient

            client = PhantomBusterClient()
            assert hasattr(client, "launch_agent")
            assert callable(client.launch_agent)

    @pytest.mark.asyncio
    async def test_get_agent_output_method_exists(self):
        """Test get_agent_output method exists."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import PhantomBusterClient

            client = PhantomBusterClient()
            assert hasattr(client, "get_agent_output")
            assert callable(client.get_agent_output)

    @pytest.mark.asyncio
    async def test_scrape_linkedin_profile_method_exists(self):
        """Test scrape_linkedin_profile method exists."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import PhantomBusterClient

            client = PhantomBusterClient()
            assert hasattr(client, "scrape_linkedin_profile")
            assert callable(client.scrape_linkedin_profile)

    @pytest.mark.asyncio
    async def test_send_linkedin_message_method_exists(self):
        """Test send_linkedin_message method exists."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import PhantomBusterClient

            client = PhantomBusterClient()
            assert hasattr(client, "send_linkedin_message")
            assert callable(client.send_linkedin_message)

    @pytest.mark.asyncio
    async def test_launch_agent_mocked(self):
        """Test launch_agent with mocked API."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import PhantomBusterClient

            client = PhantomBusterClient()

            # Mock the API call
            mock_response = {"status": "success", "data": {"containerId": "abc123"}}
            client._request_v1 = AsyncMock(return_value={"containerId": "abc123"})

            result = await client.launch_agent("12345", {"test": "arg"})
            assert result == "abc123"

    @pytest.mark.asyncio
    async def test_get_agent_output_mocked(self):
        """Test get_agent_output with mocked API."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import (
                PhantomBusterClient,
                AgentStatus,
            )

            client = PhantomBusterClient()

            # Mock the API call
            client._request_v2 = AsyncMock(
                return_value={
                    "containerId": "abc123",
                    "status": "finished",
                    "resultObject": {"success": True},
                    "output": "Done",
                    "exitCode": 0,
                }
            )

            output = await client.get_agent_output("12345")
            assert output.container_id == "abc123"
            assert output.status == AgentStatus.FINISHED
            assert output.result_object == {"success": True}
            assert output.exit_code == 0

    @pytest.mark.asyncio
    async def test_scrape_linkedin_profile_mocked(self):
        """Test scrape_linkedin_profile with mocked API."""
        with patch.dict(
            "os.environ",
            {
                "PHANTOMBUSTER_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "OPENAI_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.integrations.phantombuster import (
                PhantomBusterClient,
                AgentOutput,
                AgentStatus,
            )

            client = PhantomBusterClient()

            # Mock launch_and_wait
            client.launch_and_wait = AsyncMock(
                return_value=AgentOutput(
                    container_id="abc123",
                    status=AgentStatus.FINISHED,
                    result_object={
                        "firstName": "John",
                        "lastName": "Doe",
                        "company": "Test Corp",
                        "jobTitle": "CSR Manager",
                        "headline": "Helping companies succeed",
                        "location": "Tel Aviv",
                    },
                )
            )

            profile = await client.scrape_linkedin_profile(
                "scraper123", "https://linkedin.com/in/johndoe"
            )

            assert profile.first_name == "John"
            assert profile.last_name == "Doe"
            assert profile.full_name == "John Doe"
            assert profile.company == "Test Corp"
            assert profile.position == "CSR Manager"
            assert profile.linkedin_url == "https://linkedin.com/in/johndoe"


class TestAgentStatus:
    """Test AgentStatus enum."""

    def test_all_statuses_defined(self):
        """Test all expected statuses are defined."""
        from src.integrations.phantombuster import AgentStatus

        assert hasattr(AgentStatus, "RUNNING")
        assert hasattr(AgentStatus, "FINISHED")
        assert hasattr(AgentStatus, "ERROR")
        assert hasattr(AgentStatus, "LAUNCHING")
