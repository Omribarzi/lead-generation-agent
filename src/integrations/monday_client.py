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


@dataclass
class Lead:
    """Represents a lead in the Monday.com board."""

    name: str
    company: str
    position: str
    linkedin_url: str
    status: str = "New"
    last_message_date: Optional[str] = None
    conversation_log: str = ""
    lead_score: int = 0
    item_id: Optional[str] = None


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
        # Build column values
        column_values = {
            "text": lead.company,  # Company column
            "text6": lead.position,  # Position column
            "link": {"url": lead.linkedin_url, "text": "LinkedIn"},  # LinkedIn URL column
            "status": {"label": lead.status},  # Status column
        }

        if lead.conversation_log:
            column_values["long_text"] = {"text": lead.conversation_log}

        if lead.lead_score:
            column_values["numbers"] = lead.lead_score

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
            "item_name": lead.name,
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
        column_values = {"status": {"label": status}}

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
            status_col = columns.get("status", {})
            item_status = status_col.get("text", "")

            if item_status == status:
                lead = Lead(
                    name=item["name"],
                    company=columns.get("text", {}).get("text", ""),
                    position=columns.get("text6", {}).get("text", ""),
                    linkedin_url=self._extract_url(columns.get("link", {}).get("value")),
                    status=item_status,
                    conversation_log=columns.get("long_text", {}).get("text", ""),
                    item_id=item["id"],
                )
                leads.append(lead)

        return leads

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
                if cv["id"] == "long_text":
                    current_log = cv.get("text", "") or ""
                    break

        # Append new message with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_log = f"{current_log}\n\n[{timestamp}]\n{message}".strip()

        # Update the column
        column_values = {"long_text": {"text": new_log}}

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
        column_values = {"date": {"date": today}}

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

        return Lead(
            name=item["name"],
            company=columns.get("text", {}).get("text", ""),
            position=columns.get("text6", {}).get("text", ""),
            linkedin_url=self._extract_url(columns.get("link", {}).get("value")),
            status=columns.get("status", {}).get("text", ""),
            conversation_log=columns.get("long_text", {}).get("text", ""),
            item_id=item["id"],
        )

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
