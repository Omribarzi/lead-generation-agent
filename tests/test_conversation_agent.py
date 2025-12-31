"""Tests for AI Conversation Agent."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestConversationAgent:
    """Test ConversationAgent class."""

    def test_import_conversation_agent(self):
        """Test that ConversationAgent can be imported."""
        from src.agents.conversation_agent import ConversationAgent

        assert ConversationAgent is not None

    def test_import_message_type(self):
        """Test that MessageType enum can be imported."""
        from src.agents.conversation_agent import MessageType

        assert MessageType.FIRST_OUTREACH == "first_outreach"
        assert MessageType.FOLLOW_UP == "follow_up"
        assert MessageType.REPLY == "reply"
        assert MessageType.MEETING_REQUEST == "meeting_request"

    def test_lead_context_dataclass(self):
        """Test LeadContext dataclass."""
        from src.agents.conversation_agent import LeadContext

        lead = LeadContext(
            first_name="יוסי",
            last_name="כהן",
            company="חברה בע״מ",
            position="מנהל משאבי אנוש",
            linkedin_url="https://linkedin.com/in/test",
            headline="מנהל HR מנוסה",
        )

        assert lead.first_name == "יוסי"
        assert lead.last_name == "כהן"
        assert lead.full_name == "יוסי כהן"
        assert lead.company == "חברה בע״מ"
        assert lead.position == "מנהל משאבי אנוש"
        assert lead.conversation_history == []

    def test_generated_message_dataclass(self):
        """Test GeneratedMessage dataclass."""
        from src.agents.conversation_agent import GeneratedMessage, MessageType

        message = GeneratedMessage(
            content="שלום יוסי, ראיתי שאתה עובד בחברה בע״מ.",
            message_type=MessageType.FIRST_OUTREACH,
            word_count=7,
            is_valid=True,
            validation_errors=[],
        )

        assert message.content == "שלום יוסי, ראיתי שאתה עובד בחברה בע״מ."
        assert message.message_type == MessageType.FIRST_OUTREACH
        assert message.word_count == 7
        assert message.is_valid is True
        assert message.validation_errors == []

    def test_client_initialization(self):
        """Test agent initializes with settings."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent

            agent = ConversationAgent()
            assert agent is not None
            assert agent.api_key == "test_key"
            assert agent.model == "gpt-5-mini"
            assert agent.advanced_model == "gpt-5.2"

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        from src.agents.conversation_agent import SYSTEM_PROMPT

        assert SYSTEM_PROMPT is not None
        assert "גיא" in SYSTEM_PROMPT
        assert "מגדלור" in SYSTEM_PROMPT
        assert "קשרים" in SYSTEM_PROMPT
        assert "30" in SYSTEM_PROMPT  # Max words

    def test_message_templates_exist(self):
        """Test that message templates are defined."""
        from src.agents.conversation_agent import (
            FIRST_MESSAGE_TEMPLATE,
            FOLLOW_UP_TEMPLATE,
            REPLY_TEMPLATE,
            MEETING_REQUEST_TEMPLATE,
        )

        assert FIRST_MESSAGE_TEMPLATE is not None
        assert FOLLOW_UP_TEMPLATE is not None
        assert REPLY_TEMPLATE is not None
        assert MEETING_REQUEST_TEMPLATE is not None

    @pytest.mark.asyncio
    async def test_generate_message_method_exists(self):
        """Test generate_message method exists."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent

            agent = ConversationAgent()
            assert hasattr(agent, "generate_message")
            assert callable(agent.generate_message)

    @pytest.mark.asyncio
    async def test_generate_first_message_method_exists(self):
        """Test generate_first_message method exists."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent

            agent = ConversationAgent()
            assert hasattr(agent, "generate_first_message")
            assert callable(agent.generate_first_message)

    @pytest.mark.asyncio
    async def test_generate_follow_up_method_exists(self):
        """Test generate_follow_up method exists."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent

            agent = ConversationAgent()
            assert hasattr(agent, "generate_follow_up")
            assert callable(agent.generate_follow_up)

    @pytest.mark.asyncio
    async def test_generate_reply_method_exists(self):
        """Test generate_reply method exists."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent

            agent = ConversationAgent()
            assert hasattr(agent, "generate_reply")
            assert callable(agent.generate_reply)

    @pytest.mark.asyncio
    async def test_generate_meeting_request_method_exists(self):
        """Test generate_meeting_request method exists."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent

            agent = ConversationAgent()
            assert hasattr(agent, "generate_meeting_request")
            assert callable(agent.generate_meeting_request)


class TestMessageValidation:
    """Test message validation logic."""

    def test_validate_word_count(self):
        """Test word count validation."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent, MessageType

            agent = ConversationAgent()

            # Valid message (under 30 words)
            is_valid, errors = agent._validate_message(
                "שלום יוסי, ראיתי שאתה מנהל HR בחברה.", MessageType.FIRST_OUTREACH
            )
            assert is_valid is True

            # Invalid message (over 35 words)
            long_message = " ".join(["מילה"] * 40)
            is_valid, errors = agent._validate_message(
                long_message, MessageType.FIRST_OUTREACH
            )
            assert is_valid is False
            assert any("מילים" in error for error in errors)

    def test_validate_dashes(self):
        """Test dash validation."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent, MessageType

            agent = ConversationAgent()

            # Valid message (no dashes)
            is_valid, errors = agent._validate_message(
                "שלום יוסי, מה שלומך?", MessageType.FIRST_OUTREACH
            )
            assert "מקפים" not in str(errors)

            # Invalid message (with dash)
            is_valid, errors = agent._validate_message(
                "שלום יוסי - מה שלומך?", MessageType.FIRST_OUTREACH
            )
            assert is_valid is False
            assert any("מקפים" in error for error in errors)

    def test_validate_first_message_no_meeting(self):
        """Test first message doesn't ask for meeting."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent, MessageType

            agent = ConversationAgent()

            # Valid first message (no meeting request)
            is_valid, errors = agent._validate_message(
                "שלום יוסי, ראיתי שאתה עובד בהייטק.",
                MessageType.FIRST_OUTREACH,
            )
            assert "פגישה" not in str(errors)

            # Invalid first message (asks for meeting)
            is_valid, errors = agent._validate_message(
                "שלום יוסי, אשמח לקבוע פגישה איתך.",
                MessageType.FIRST_OUTREACH,
            )
            assert is_valid is False
            assert any("פגישה" in error for error in errors)

    def test_validate_first_message_no_flattery(self):
        """Test first message doesn't have flattery words."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent, MessageType

            agent = ConversationAgent()

            # Invalid first message (with flattery)
            is_valid, errors = agent._validate_message(
                "שלום יוסי, הקריירה שלך מרשים מאוד!",
                MessageType.FIRST_OUTREACH,
            )
            assert is_valid is False
            assert any("חנופה" in error for error in errors)

    def test_validate_empty_message(self):
        """Test empty message validation."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import ConversationAgent, MessageType

            agent = ConversationAgent()

            is_valid, errors = agent._validate_message("", MessageType.FIRST_OUTREACH)
            assert is_valid is False
            assert any("ריקה" in error for error in errors)


class TestPromptBuilding:
    """Test prompt building logic."""

    def test_build_first_outreach_prompt(self):
        """Test building first outreach prompt."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()
            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
                headline="מנהל משאבי אנוש מנוסה",
            )

            prompt = agent._build_prompt(lead, MessageType.FIRST_OUTREACH)

            assert "יוסי כהן" in prompt
            assert "מנהל HR" in prompt
            assert "חברה בע״מ" in prompt
            assert "מנהל משאבי אנוש מנוסה" in prompt

    def test_build_follow_up_prompt_with_history(self):
        """Test building follow-up prompt with conversation history."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()
            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
                conversation_history=[
                    {"sender": "us", "content": "שלום יוסי!"},
                ],
            )

            prompt = agent._build_prompt(lead, MessageType.FOLLOW_UP)

            assert "יוסי כהן" in prompt
            assert "אני: שלום יוסי!" in prompt

    def test_build_reply_prompt(self):
        """Test building reply prompt."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()
            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
            )

            prompt = agent._build_prompt(
                lead, MessageType.REPLY, last_message="מעניין, ספר לי עוד"
            )

            assert "יוסי כהן" in prompt
            assert "מעניין, ספר לי עוד" in prompt

    def test_build_meeting_request_prompt(self):
        """Test building meeting request prompt."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()
            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
            )

            prompt = agent._build_prompt(lead, MessageType.MEETING_REQUEST)

            assert "יוסי כהן" in prompt
            assert "calendar.google.com" in prompt


class TestMockedGeneration:
    """Test message generation with mocked OpenAI API."""

    @pytest.mark.asyncio
    async def test_generate_first_message_mocked(self):
        """Test generating first message with mocked API."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()

            # Mock the OpenAI client
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content="שלום יוסי, ראיתי שאתה עובד כמנהל HR בחברה בע״מ. מה עמדת החברה שלכם בנושא גיוס חיילים משוחררים?"
                    )
                )
            ]
            agent._client.chat.completions.create = AsyncMock(return_value=mock_response)

            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
                headline="מנהל משאבי אנוש",
            )

            message = await agent.generate_first_message(lead)

            assert message.content is not None
            assert message.message_type == MessageType.FIRST_OUTREACH
            assert message.word_count > 0

    @pytest.mark.asyncio
    async def test_generate_reply_mocked(self):
        """Test generating reply with mocked API."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()

            # Mock the OpenAI client
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content="תודה על העניין! תוכנית קשרים מחברת בין משוחררים לבוגרי קורס חובלים בתעשייה."
                    )
                )
            ]
            agent._client.chat.completions.create = AsyncMock(return_value=mock_response)

            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
                conversation_history=[
                    {"sender": "us", "content": "שלום יוסי!"},
                    {"sender": "them", "content": "היי, מה זו תוכנית קשרים?"},
                ],
            )

            message = await agent.generate_reply(lead, "מה זו תוכנית קשרים?")

            assert message.content is not None
            assert message.message_type == MessageType.REPLY

    @pytest.mark.asyncio
    async def test_regenerate_if_invalid_mocked(self):
        """Test regeneration when message is invalid."""
        with patch.dict(
            "os.environ",
            {
                "OPENAI_API_KEY": "test_key",
                "MONDAY_API_KEY": "test",
                "MONDAY_BOARD_ID": "12345",
                "PHANTOMBUSTER_API_KEY": "test",
            },
        ):
            from src.config.settings import get_settings

            get_settings.cache_clear()

            from src.agents.conversation_agent import (
                ConversationAgent,
                LeadContext,
                MessageType,
            )

            agent = ConversationAgent()

            # First call returns invalid message (with dash), second returns valid
            mock_responses = [
                MagicMock(
                    choices=[
                        MagicMock(message=MagicMock(content="שלום - איך אתה?"))
                    ]
                ),
                MagicMock(
                    choices=[
                        MagicMock(message=MagicMock(content="שלום יוסי, מה שלומך?"))
                    ]
                ),
            ]
            agent._client.chat.completions.create = AsyncMock(side_effect=mock_responses)

            lead = LeadContext(
                first_name="יוסי",
                last_name="כהן",
                company="חברה בע״מ",
                position="מנהל HR",
                linkedin_url="https://linkedin.com/in/test",
            )

            message = await agent.regenerate_if_invalid(
                lead, MessageType.FIRST_OUTREACH, max_attempts=2
            )

            # Should get the valid second message
            assert message.is_valid is True
            assert "שלום יוסי" in message.content
