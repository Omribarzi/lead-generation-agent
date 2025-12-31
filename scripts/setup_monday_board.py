#!/usr/bin/env python3
"""
Setup Monday.com CRM board for Ksharim Lead Generation.

This script creates a new board with all required columns for the lead pipeline.

Columns created:
- Name (default item name)
- Company (text)
- Position (text)
- LinkedIn URL (link)
- Status (status: New, Contacted, In Conversation, Meeting Scheduled, Not Interested, Won)
- Last Message Date (date)
- Conversation Log (long text)
- Lead Score (numbers)

Usage:
    python scripts/setup_monday_board.py
"""

import asyncio
import json

import httpx

from src.config.settings import get_settings


async def create_board(client: httpx.AsyncClient, api_key: str) -> str:
    """Create a new board for the CRM.

    Returns:
        The new board ID
    """
    query = """
    mutation {
        create_board (
            board_name: "Ksharim Lead Pipeline",
            board_kind: private
        ) {
            id
        }
    }
    """

    response = await client.post(
        "https://api.monday.com/v2",
        json={"query": query},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    result = response.json()

    if "errors" in result:
        raise Exception(f"API Error: {result['errors']}")

    board_id = result["data"]["create_board"]["id"]
    print(f"Created board: Ksharim Lead Pipeline (ID: {board_id})")
    return board_id


async def create_column(
    client: httpx.AsyncClient,
    api_key: str,
    board_id: str,
    title: str,
    column_type: str,
    defaults: dict = None
) -> str:
    """Create a column on the board.

    Args:
        client: HTTP client
        api_key: Monday.com API key
        board_id: The board ID
        title: Column title
        column_type: Column type (text, link, status, date, long_text, numbers)
        defaults: Default values for status columns

    Returns:
        The column ID
    """
    query = """
    mutation ($board_id: ID!, $title: String!, $column_type: ColumnType!, $defaults: JSON) {
        create_column (
            board_id: $board_id,
            title: $title,
            column_type: $column_type,
            defaults: $defaults
        ) {
            id
            title
        }
    }
    """

    variables = {
        "board_id": board_id,
        "title": title,
        "column_type": column_type,
    }

    if defaults:
        variables["defaults"] = json.dumps(defaults)

    response = await client.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers={
            "Authorization": api_key,
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    result = response.json()

    if "errors" in result:
        raise Exception(f"API Error creating column '{title}': {result['errors']}")

    column_id = result["data"]["create_column"]["id"]
    print(f"  Created column: {title} ({column_type}) -> {column_id}")
    return column_id


async def setup_board():
    """Set up the complete CRM board with all columns."""
    settings = get_settings()
    api_key = settings.MONDAY_API_KEY

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Create the board
        print("\n=== Setting up Ksharim Lead Pipeline Board ===\n")
        board_id = await create_board(client, api_key)

        print("\nCreating columns...")

        # Create columns
        columns = {}

        # Company (text)
        columns["company"] = await create_column(
            client, api_key, board_id,
            "Company", "text"
        )

        # Position (text)
        columns["position"] = await create_column(
            client, api_key, board_id,
            "Position", "text"
        )

        # LinkedIn URL (link)
        columns["linkedin"] = await create_column(
            client, api_key, board_id,
            "LinkedIn URL", "link"
        )

        # Status (status with labels)
        status_defaults = {
            "labels": {
                "0": "New",
                "1": "Contacted",
                "2": "In Conversation",
                "3": "Meeting Scheduled",
                "4": "Not Interested",
                "5": "Won"
            },
            "labels_colors": {
                "0": {"color": "#579bfc", "border": "#4387E8", "var_name": "blue"},
                "1": {"color": "#fdab3d", "border": "#E99729", "var_name": "orange"},
                "2": {"color": "#ffcb00", "border": "#E0B500", "var_name": "yellow"},
                "3": {"color": "#00c875", "border": "#00AB66", "var_name": "green"},
                "4": {"color": "#df2f4a", "border": "#C8283D", "var_name": "red"},
                "5": {"color": "#9cd326", "border": "#89BA1F", "var_name": "lime-green"}
            }
        }
        columns["status"] = await create_column(
            client, api_key, board_id,
            "Status", "status",
            status_defaults
        )

        # Last Message Date (date)
        columns["last_message"] = await create_column(
            client, api_key, board_id,
            "Last Message Date", "date"
        )

        # Conversation Log (long text)
        columns["conversation"] = await create_column(
            client, api_key, board_id,
            "Conversation Log", "long_text"
        )

        # Lead Score (numbers)
        columns["score"] = await create_column(
            client, api_key, board_id,
            "Lead Score", "numbers"
        )

        print("\n=== Board Setup Complete ===")
        print(f"\nBoard ID: {board_id}")
        print("\nUpdate your .env file with:")
        print(f"MONDAY_BOARD_ID={board_id}")
        print("\nColumn IDs for reference:")
        for name, col_id in columns.items():
            print(f"  {name}: {col_id}")

        return board_id, columns


if __name__ == "__main__":
    board_id, columns = asyncio.run(setup_board())
