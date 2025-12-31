"""
Monday.com API client for lead management.

This module provides a client for interacting with the Monday.com API
to manage leads in the Ksharim CRM board.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import httpx

from src.config.settings import get_settings


# Lead status constants
LEAD_STATUS = {
    "NEW": "New",
    "CONTACTED": "Contacted",
    "IN_CONVERSATION": "In Conversation",
    "MEETING_SCHEDULED": "Meeting Scheduled",
    "NOT_INTERESTED": "Not Interested",
    "WON": "Won",
}

# Lead source constants
LEAD_SOURCES = [
    "LinkedIn Search",
    "LinkedIn Sales Navigator",
    "Referral",
    "Website",
    "Event",
    "Other",
]

# Column IDs for the Ksharim Lead Pipeline board
COLUMN_IDS = {
    "first_name": "text_mkz5ee4p",
    "last_name": "text_mkz5z85j",
    "company": "text_mkz58xs9",
    "position": "text_mkz55gcc",
    "linkedin": "link_mkz5m6nn",
    "status": "color_mkz5scfr",
    "last_message": "date_mkz58sks",
    "conversation": "long_text_mkz56sc2",
    "score": "numeric_mkz5p3m6",
    "email": "email_mkz5ram4",
    "phone": "phone_mkz5jdqh",
    "notes": "long_text_mkz5pgk0",
    "next_action": "date_mkz5ddwy",
    "meeting_date": "date_mkz5x0cj",
    "source": "color_mkz5w950",
}


@dataclass
class Lead:
    """Represents a lead in the Monday.com board."""

    first_name: str
    last_name: str
    company: str
    position: str
    linkedin_url: str
    status: str = "New"
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    last_message_date: Optional[str] = None
    next_action_date: Optional[str] = None
    meeting_date: Optional[str] = None
    conversation_log: str = ""
    notes: str = ""
    lead_score: int = 0
    item_id: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Return the full name of the lead."""
        return f"{self.first_name} {self.last_name}".strip()


class MondayClient:
    """Client for interacting with Monday.com API."""

    API_URL = "https://api.monday.com/v2"

    def __init__(self):
        """Initialize the Monday.com client."""
        settings = get_settings()
        self.api_key = settings.MONDAY_API_KEY
        self.board_id = settings.MONDAY_BOARD_ID
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def _execute_query(self, query: str, variables: Optional[dict] = None) -> dict:
        """Execute a GraphQL query against the Monday.com API.

        Args:
            query: The GraphQL query string
            variables: Optional variables for the query

        Returns:
            The JSON response from the API
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        response = await self._client.post(self.API_URL, json=payload)
        response.raise_for_status()
        return response.json()

    async def create_lead(self, lead: Lead) -> str:
        """Create a new lead in the Monday.com board.

        Args:
            lead: The Lead object to create

        Returns:
            The ID of the created item
        """
        # Build column values using correct column IDs
        column_values = {
            COLUMN_IDS["first_name"]: lead.first_name,
            COLUMN_IDS["last_name"]: lead.last_name,
            COLUMN_IDS["company"]: lead.company,
            COLUMN_IDS["position"]: lead.position,
            COLUMN_IDS["linkedin"]: {"url": lead.linkedin_url, "text": "LinkedIn"},
            COLUMN_IDS["status"]: {"label": lead.status},
        }

        # Optional fields
        if lead.email:
            column_values[COLUMN_IDS["email"]] = {"email": lead.email, "text": lead.email}

        if lead.phone:
            column_values[COLUMN_IDS["phone"]] = {"phone": lead.phone}

        if lead.source:
            column_values[COLUMN_IDS["source"]] = {"label": lead.source}

        if lead.conversation_log:
            column_values[COLUMN_IDS["conversation"]] = {"text": lead.conversation_log}

        if lead.notes:
            column_values[COLUMN_IDS["notes"]] = {"text": lead.notes}

        if lead.lead_score:
            column_values[COLUMN_IDS["score"]] = lead.lead_score

        if lead.next_action_date:
            column_values[COLUMN_IDS["next_action"]] = {"date": lead.next_action_date}

        if lead.meeting_date:
            column_values[COLUMN_IDS["meeting_date"]] = {"date": lead.meeting_date}

        query = """
        mutation ($board_id: ID!, $item_name: String!, $column_values: JSON!) {
            create_item (
                board_id: $board_id,
                item_name: $item_name,
                column_values: $column_values
            ) {
                id
            }
        }
        """

        variables = {
            "board_id": self.board_id,
            "item_name": lead.full_name,
            "column_values": json.dumps(column_values),
        }

        result = await self._execute_query(query, variables)
        return result["data"]["create_item"]["id"]

    async def update_lead_status(self, item_id: str, status: str) -> bool:
        """Update the status of a lead.

        Args:
            item_id: The ID of the item to update
            status: The new status value

        Returns:
            True if successful
        """
        column_values = {COLUMN_IDS["status"]: {"label": status}}

        query = """
        mutation ($board_id: ID!, $item_id: ID!, $column_values: JSON!) {
            change_multiple_column_values (
                board_id: $board_id,
                item_id: $item_id,
                column_values: $column_values
            ) {
                id
            }
        }
        """

        variables = {
            "board_id": self.board_id,
            "item_id": item_id,
            "column_values": json.dumps(column_values),
        }

        await self._execute_query(query, variables)
        return True

    async def update_lead(self, item_id: str, **kwargs) -> bool:
        """Update multiple fields on a lead.

        Args:
            item_id: The ID of the item to update
            **kwargs: Field names and values to update

        Returns:
            True if successful
        """
        column_values = {}

        field_mapping = {
            "first_name": (COLUMN_IDS["first_name"], lambda v: v),
            "last_name": (COLUMN_IDS["last_name"], lambda v: v),
            "status": (COLUMN_IDS["status"], lambda v: {"label": v}),
            "email": (COLUMN_IDS["email"], lambda v: {"email": v, "text": v}),
            "phone": (COLUMN_IDS["phone"], lambda v: {"phone": v}),
            "source": (COLUMN_IDS["source"], lambda v: {"label": v}),
            "notes": (COLUMN_IDS["notes"], lambda v: {"text": v}),
            "next_action_date": (COLUMN_IDS["next_action"], lambda v: {"date": v}),
            "meeting_date": (COLUMN_IDS["meeting_date"], lambda v: {"date": v}),
            "lead_score": (COLUMN_IDS["score"], lambda v: v),
            "company": (COLUMN_IDS["company"], lambda v: v),
            "position": (COLUMN_IDS["position"], lambda v: v),
        }

        for field_name, value in kwargs.items():
            if field_name in field_mapping and value is not None:
                col_id, transformer = field_mapping[field_name]
                column_values[col_id] = transformer(value)

        if not column_values:
            return True

        query = """
        mutation ($board_id: ID!, $item_id: ID!, $column_values: JSON!) {
            change_multiple_column_values (
                board_id: $board_id,
                item_id: $item_id,
                column_values: $column_values
            ) {
                id
            }
        }
        """

        variables = {
            "board_id": self.board_id,
            "item_id": item_id,
            "column_values": json.dumps(column_values),
        }

        await self._execute_query(query, variables)
        return True

    async def get_leads_by_status(self, status: str) -> list[Lead]:
        """Get all leads with a specific status.

        Args:
            status: The status to filter by

        Returns:
            List of Lead objects
        """
        query = """
        query ($board_id: ID!) {
            boards (ids: [$board_id]) {
                items_page (limit: 100) {
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
        """

        variables = {"board_id": self.board_id}
        result = await self._execute_query(query, variables)

        leads = []
        items = result.get("data", {}).get("boards", [{}])[0].get("items_page", {}).get("items", [])

        for item in items:
            # Parse column values
            columns = {cv["id"]: cv for cv in item.get("column_values", [])}

            # Check if status matches
            status_col = columns.get(COLUMN_IDS["status"], {})
            item_status = status_col.get("text", "")

            if item_status == status:
                lead = self._parse_lead_from_item(item, columns)
                leads.append(lead)

        return leads

    async def get_all_leads(self) -> list[Lead]:
        """Get all leads from the board.

        Returns:
            List of Lead objects
        """
        query = """
        query ($board_id: ID!) {
            boards (ids: [$board_id]) {
                items_page (limit: 500) {
                    items {
                        id
                        name
                        column_values {
                            id
                            text
                            value
                        }
                    }
                }
            }
        }
        """

        variables = {"board_id": self.board_id}
        result = await self._execute_query(query, variables)

        leads = []
        items = result.get("data", {}).get("boards", [{}])[0].get("items_page", {}).get("items", [])

        for item in items:
            columns = {cv["id"]: cv for cv in item.get("column_values", [])}
            lead = self._parse_lead_from_item(item, columns)
            leads.append(lead)

        return leads

    def _parse_lead_from_item(self, item: dict, columns: dict) -> Lead:
        """Parse a Lead object from Monday.com item data.

        Args:
            item: The item data from the API
            columns: Dictionary of column values by ID

        Returns:
            Lead object
        """
        # Get first_name and last_name from columns, fallback to parsing item name
        first_name = columns.get(COLUMN_IDS["first_name"], {}).get("text", "")
        last_name = columns.get(COLUMN_IDS["last_name"], {}).get("text", "")

        # If columns are empty, try to parse from item name (for backward compatibility)
        if not first_name and not last_name and item.get("name"):
            name_parts = item["name"].split(" ", 1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""

        return Lead(
            first_name=first_name,
            last_name=last_name,
            company=columns.get(COLUMN_IDS["company"], {}).get("text", ""),
            position=columns.get(COLUMN_IDS["position"], {}).get("text", ""),
            linkedin_url=self._extract_url(columns.get(COLUMN_IDS["linkedin"], {}).get("value")),
            status=columns.get(COLUMN_IDS["status"], {}).get("text", ""),
            email=columns.get(COLUMN_IDS["email"], {}).get("text", ""),
            phone=columns.get(COLUMN_IDS["phone"], {}).get("text", ""),
            source=columns.get(COLUMN_IDS["source"], {}).get("text", ""),
            last_message_date=columns.get(COLUMN_IDS["last_message"], {}).get("text", ""),
            next_action_date=columns.get(COLUMN_IDS["next_action"], {}).get("text", ""),
            meeting_date=columns.get(COLUMN_IDS["meeting_date"], {}).get("text", ""),
            conversation_log=columns.get(COLUMN_IDS["conversation"], {}).get("text", ""),
            notes=columns.get(COLUMN_IDS["notes"], {}).get("text", ""),
            lead_score=self._parse_number(columns.get(COLUMN_IDS["score"], {}).get("text", "")),
            item_id=item["id"],
        )

    def _parse_number(self, value: str) -> int:
        """Parse a number from string, returning 0 if invalid."""
        try:
            return int(float(value)) if value else 0
        except (ValueError, TypeError):
            return 0

    async def append_to_conversation_log(self, item_id: str, message: str) -> bool:
        """Append a message to the conversation log of a lead.

        Args:
            item_id: The ID of the item to update
            message: The message to append

        Returns:
            True if successful
        """
        # First, get the current conversation log
        query = """
        query ($item_id: ID!) {
            items (ids: [$item_id]) {
                column_values {
                    id
                    text
                }
            }
        }
        """

        result = await self._execute_query(query, {"item_id": item_id})
        items = result.get("data", {}).get("items", [])

        current_log = ""
        if items:
            for cv in items[0].get("column_values", []):
                if cv["id"] == COLUMN_IDS["conversation"]:
                    current_log = cv.get("text", "") or ""
                    break

        # Append new message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_log = f"{current_log}\n\n[{timestamp}]\n{message}".strip()

        # Update the column
        column_values = {COLUMN_IDS["conversation"]: {"text": new_log}}

        update_query = """
        mutation ($board_id: ID!, $item_id: ID!, $column_values: JSON!) {
            change_multiple_column_values (
                board_id: $board_id,
                item_id: $item_id,
                column_values: $column_values
            ) {
                id
            }
        }
        """

        variables = {
            "board_id": self.board_id,
            "item_id": item_id,
            "column_values": json.dumps(column_values),
        }

        await self._execute_query(update_query, variables)
        return True

    async def update_last_message_date(self, item_id: str) -> bool:
        """Update the last message date to today.

        Args:
            item_id: The ID of the item to update

        Returns:
            True if successful
        """
        today = datetime.now().strftime("%Y-%m-%d")
        column_values = {COLUMN_IDS["last_message"]: {"date": today}}

        query = """
        mutation ($board_id: ID!, $item_id: ID!, $column_values: JSON!) {
            change_multiple_column_values (
                board_id: $board_id,
                item_id: $item_id,
                column_values: $column_values
            ) {
                id
            }
        }
        """

        variables = {
            "board_id": self.board_id,
            "item_id": item_id,
            "column_values": json.dumps(column_values),
        }

        await self._execute_query(query, variables)
        return True

    async def set_meeting_date(self, item_id: str, meeting_date: str) -> bool:
        """Set the meeting date for a lead.

        Args:
            item_id: The ID of the item to update
            meeting_date: The meeting date in YYYY-MM-DD format

        Returns:
            True if successful
        """
        return await self.update_lead(item_id, meeting_date=meeting_date)

    async def set_next_action_date(self, item_id: str, next_action_date: str) -> bool:
        """Set the next action date for a lead.

        Args:
            item_id: The ID of the item to update
            next_action_date: The next action date in YYYY-MM-DD format

        Returns:
            True if successful
        """
        return await self.update_lead(item_id, next_action_date=next_action_date)

    async def get_lead_by_id(self, item_id: str) -> Optional[Lead]:
        """Get a lead by its item ID.

        Args:
            item_id: The ID of the item

        Returns:
            Lead object or None if not found
        """
        query = """
        query ($item_id: ID!) {
            items (ids: [$item_id]) {
                id
                name
                column_values {
                    id
                    text
                    value
                }
            }
        }
        """

        result = await self._execute_query(query, {"item_id": item_id})
        items = result.get("data", {}).get("items", [])

        if not items:
            return None

        item = items[0]
        columns = {cv["id"]: cv for cv in item.get("column_values", [])}

        return self._parse_lead_from_item(item, columns)

    def _extract_url(self, value: Optional[str]) -> str:
        """Extract URL from Monday.com link column value.

        Args:
            value: The JSON string value from the link column

        Returns:
            The URL string or empty string
        """
        if not value:
            return ""
        try:
            data = json.loads(value)
            return data.get("url", "")
        except (json.JSONDecodeError, TypeError):
            return ""

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
