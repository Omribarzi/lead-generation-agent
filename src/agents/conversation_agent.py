"""
AI Conversation Agent for LinkedIn outreach.

Uses OpenAI API to generate personalized Hebrew messages for the Ksharim program.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from openai import AsyncOpenAI

from src.config.settings import get_settings


class MessageType(str, Enum):
    """Type of message in the conversation."""

    FIRST_OUTREACH = "first_outreach"
    FOLLOW_UP = "follow_up"
    REPLY = "reply"
    MEETING_REQUEST = "meeting_request"


@dataclass
class LeadContext:
    """Context about a lead for message generation."""

    first_name: str
    last_name: str
    company: str
    position: str
    linkedin_url: str
    headline: str = ""
    summary: str = ""
    location: str = ""
    conversation_history: list[dict] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        """Return the full name."""
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class GeneratedMessage:
    """Result of message generation."""

    content: str
    message_type: MessageType
    word_count: int
    is_valid: bool
    validation_errors: list[str] = field(default_factory=list)


# System prompt for the AI agent (from CLAUDE.md)
SYSTEM_PROMPT = """אתה גיא ממגדלור - ארגון בוגרי קורס חובלים.

כללים:
- עברית בלבד
- מקסימום 30 מילים בהודעה
- ללא מקפים (השתמש בפסיק או נקודה)
- לעולם אל תתחיל במילת פועל
- טון דיבור, פרגמטי
- מקסימום 2 שאלות בשיחה
- לעולם אל תבקש פגישה בהודעה ראשונה

כללים להודעה ראשונה:
- ברך בשם
- התייחס לפרט אחד ספציפי מהפרופיל שלהם
- ללא מילות חנופה (מרשים, מעריץ, אוהב)
- סיים בשאלה אחת נועזת על CSR/אחריות חברתית

מה אנחנו מציעים:
תוכנית "קשרים" של מגדלור מחברת בין חיילים משוחררים לבוגרי קורס החובלים שלנו בתעשייה של פיננסים, הייטק ועסקים, ומסייעת למשוחררים להתקדם בקריירה."""


FIRST_MESSAGE_TEMPLATE = """צור הודעת לינקדאין ראשונה עבור:
שם: {full_name}
תפקיד: {position}
חברה: {company}
כותרת: {headline}
סיכום: {summary}
מיקום: {location}

זכור: עברית בלבד, מקסימום 30 מילים, ללא מקפים, לא להתחיל בפועל, טון דיבור פרגמטי."""


FOLLOW_UP_TEMPLATE = """צור הודעת המשך (follow-up) עבור:
שם: {full_name}
תפקיד: {position}
חברה: {company}

היסטוריית שיחה:
{conversation_history}

זכור: עברית בלבד, מקסימום 30 מילים, ללא מקפים, לא להתחיל בפועל, טון דיבור פרגמטי."""


REPLY_TEMPLATE = """צור תגובה להודעה שקיבלנו מ:
שם: {full_name}
תפקיד: {position}
חברה: {company}

היסטוריית שיחה:
{conversation_history}

ההודעה האחרונה שלהם:
{last_message}

זכור: עברית בלבד, מקסימום 30 מילים, ללא מקפים, לא להתחיל בפועל, טון דיבור פרגמטי."""


MEETING_REQUEST_TEMPLATE = """צור הודעה לבקשת פגישה עבור:
שם: {full_name}
תפקיד: {position}
חברה: {company}

היסטוריית שיחה:
{conversation_history}

קישור ליומן: {calendar_link}

זכור: עברית בלבד, מקסימום 30 מילים, ללא מקפים, לא להתחיל בפועל, טון דיבור פרגמטי."""


class ConversationAgent:
    """AI agent for generating LinkedIn conversation messages."""

    def __init__(self):
        """Initialize the conversation agent."""
        settings = get_settings()
        self.api_key = settings.OPENAI_API_KEY
        self.calendar_link = settings.CALENDAR_BOOKING_LINK
        self._client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4o"  # Use GPT-4o for best Hebrew support

    async def generate_message(
        self,
        lead: LeadContext,
        message_type: MessageType = MessageType.FIRST_OUTREACH,
        last_message: Optional[str] = None,
    ) -> GeneratedMessage:
        """Generate a message for a lead.

        Args:
            lead: Context about the lead
            message_type: Type of message to generate
            last_message: Last message from the lead (for replies)

        Returns:
            GeneratedMessage with content and validation status
        """
        prompt = self._build_prompt(lead, message_type, last_message)

        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
            temperature=0.7,
        )

        content = response.choices[0].message.content or ""
        content = content.strip()

        # Validate the generated message
        is_valid, errors = self._validate_message(content, message_type)

        return GeneratedMessage(
            content=content,
            message_type=message_type,
            word_count=len(content.split()),
            is_valid=is_valid,
            validation_errors=errors,
        )

    async def generate_first_message(self, lead: LeadContext) -> GeneratedMessage:
        """Generate the first outreach message for a lead.

        Args:
            lead: Context about the lead

        Returns:
            GeneratedMessage with first outreach content
        """
        return await self.generate_message(lead, MessageType.FIRST_OUTREACH)

    async def generate_follow_up(self, lead: LeadContext) -> GeneratedMessage:
        """Generate a follow-up message for a lead who didn't respond.

        Args:
            lead: Context about the lead with conversation history

        Returns:
            GeneratedMessage with follow-up content
        """
        return await self.generate_message(lead, MessageType.FOLLOW_UP)

    async def generate_reply(
        self, lead: LeadContext, their_message: str
    ) -> GeneratedMessage:
        """Generate a reply to a lead's message.

        Args:
            lead: Context about the lead with conversation history
            their_message: The message they sent us

        Returns:
            GeneratedMessage with reply content
        """
        return await self.generate_message(
            lead, MessageType.REPLY, last_message=their_message
        )

    async def generate_meeting_request(self, lead: LeadContext) -> GeneratedMessage:
        """Generate a meeting request message.

        Args:
            lead: Context about the lead with conversation history

        Returns:
            GeneratedMessage with meeting request content
        """
        return await self.generate_message(lead, MessageType.MEETING_REQUEST)

    def _build_prompt(
        self,
        lead: LeadContext,
        message_type: MessageType,
        last_message: Optional[str] = None,
    ) -> str:
        """Build the prompt for message generation.

        Args:
            lead: Context about the lead
            message_type: Type of message to generate
            last_message: Last message from the lead (for replies)

        Returns:
            Formatted prompt string
        """
        # Format conversation history
        history_str = ""
        if lead.conversation_history:
            history_lines = []
            for msg in lead.conversation_history:
                sender = "אני" if msg.get("sender") == "us" else lead.first_name
                history_lines.append(f"{sender}: {msg.get('content', '')}")
            history_str = "\n".join(history_lines)

        if message_type == MessageType.FIRST_OUTREACH:
            return FIRST_MESSAGE_TEMPLATE.format(
                full_name=lead.full_name,
                position=lead.position,
                company=lead.company,
                headline=lead.headline or "לא זמין",
                summary=lead.summary or "לא זמין",
                location=lead.location or "לא זמין",
            )
        elif message_type == MessageType.FOLLOW_UP:
            return FOLLOW_UP_TEMPLATE.format(
                full_name=lead.full_name,
                position=lead.position,
                company=lead.company,
                conversation_history=history_str or "אין היסטוריה קודמת",
            )
        elif message_type == MessageType.REPLY:
            return REPLY_TEMPLATE.format(
                full_name=lead.full_name,
                position=lead.position,
                company=lead.company,
                conversation_history=history_str or "אין היסטוריה קודמת",
                last_message=last_message or "",
            )
        else:  # MEETING_REQUEST
            return MEETING_REQUEST_TEMPLATE.format(
                full_name=lead.full_name,
                position=lead.position,
                company=lead.company,
                conversation_history=history_str or "אין היסטוריה קודמת",
                calendar_link=self.calendar_link,
            )

    def _validate_message(
        self, content: str, message_type: MessageType
    ) -> tuple[bool, list[str]]:
        """Validate a generated message against the rules.

        Args:
            content: Generated message content
            message_type: Type of message

        Returns:
            Tuple of (is_valid, list of validation errors)
        """
        errors = []

        # Check word count (max 30 words)
        word_count = len(content.split())
        if word_count > 35:  # Allow small buffer
            errors.append(f"מספר מילים גבוה מדי: {word_count} (מקסימום 30)")

        # Check for dashes (should use comma or period instead)
        if " - " in content or "–" in content or "—" in content:
            errors.append("יש מקפים בהודעה (יש להשתמש בפסיק או נקודה)")

        # Check if message is empty
        if not content.strip():
            errors.append("ההודעה ריקה")

        # For first message, check it doesn't ask for meeting
        if message_type == MessageType.FIRST_OUTREACH:
            meeting_words = ["פגישה", "להיפגש", "נפגש", "לקבוע"]
            if any(word in content for word in meeting_words):
                errors.append("הודעה ראשונה לא צריכה לבקש פגישה")

        # Check for flattery words in first message
        if message_type == MessageType.FIRST_OUTREACH:
            flattery_words = ["מרשים", "מעריץ", "אוהב", "נהדר", "מדהים", "מושלם"]
            for word in flattery_words:
                if word in content:
                    errors.append(f"יש מילת חנופה: {word}")
                    break

        return len(errors) == 0, errors

    async def regenerate_if_invalid(
        self,
        lead: LeadContext,
        message_type: MessageType = MessageType.FIRST_OUTREACH,
        last_message: Optional[str] = None,
        max_attempts: int = 3,
    ) -> GeneratedMessage:
        """Generate a message and retry if invalid.

        Args:
            lead: Context about the lead
            message_type: Type of message to generate
            last_message: Last message from the lead (for replies)
            max_attempts: Maximum number of generation attempts

        Returns:
            GeneratedMessage (best attempt if all invalid)
        """
        best_message = None

        for attempt in range(max_attempts):
            message = await self.generate_message(lead, message_type, last_message)

            if message.is_valid:
                return message

            # Keep track of the message with fewest errors
            if best_message is None or len(message.validation_errors) < len(
                best_message.validation_errors
            ):
                best_message = message

        return best_message  # type: ignore

    async def close(self):
        """Close the OpenAI client."""
        await self._client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
