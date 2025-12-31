"""
PhantomBuster API client for LinkedIn automation.

This module provides a client for interacting with the PhantomBuster API
to automate LinkedIn profile scraping and messaging.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import httpx

from src.config.settings import get_settings


class AgentStatus(str, Enum):
    """PhantomBuster agent execution status."""

    RUNNING = "running"
    FINISHED = "finished"
    ERROR = "error"
    LAUNCHING = "launching"


@dataclass
class LinkedInProfile:
    """Represents a scraped LinkedIn profile."""

    linkedin_url: str
    first_name: str = ""
    last_name: str = ""
    company: str = ""
    position: str = ""
    headline: str = ""
    location: str = ""
    profile_picture_url: str = ""
    connection_degree: str = ""
    summary: str = ""

    @property
    def full_name(self) -> str:
        """Return the full name."""
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class AgentOutput:
    """Result from a PhantomBuster agent execution."""

    container_id: str
    status: AgentStatus
    result_object: Optional[dict] = None
    output: str = ""
    exit_code: Optional[int] = None
    error_message: str = ""


class PhantomBusterClient:
    """Client for interacting with PhantomBuster API."""

    API_URL_V1 = "https://phantombuster.com/api/v1"
    API_URL_V2 = "https://api.phantombuster.com/api/v2"

    def __init__(self):
        """Initialize the PhantomBuster client."""
        settings = get_settings()
        self.api_key = settings.PHANTOMBUSTER_API_KEY
        self._client = httpx.AsyncClient(
            headers={
                "X-Phantombuster-Key-1": self.api_key,
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def _request_v1(
        self, method: str, endpoint: str, **kwargs
    ) -> dict:
        """Make a request to the v1 API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            The JSON response data
        """
        url = f"{self.API_URL_V1}{endpoint}"
        response = await self._client.request(method, url, **kwargs)
        response.raise_for_status()
        result = response.json()

        if result.get("status") == "error":
            raise Exception(f"PhantomBuster API error: {result.get('message')}")

        return result.get("data", result)

    async def _request_v2(
        self, method: str, endpoint: str, **kwargs
    ) -> dict:
        """Make a request to the v2 API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            The JSON response data
        """
        url = f"{self.API_URL_V2}{endpoint}"
        response = await self._client.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_agent(self, agent_id: str) -> dict:
        """Get agent details by ID.

        Args:
            agent_id: The PhantomBuster agent/phantom ID

        Returns:
            Agent details dictionary
        """
        return await self._request_v2("GET", f"/agents/fetch?id={agent_id}")

    async def launch_agent(
        self,
        agent_id: str,
        argument: Optional[dict] = None,
        save_argument: bool = False,
    ) -> str:
        """Launch a PhantomBuster agent.

        Args:
            agent_id: The agent/phantom ID to launch
            argument: Optional JSON arguments to pass to the agent
            save_argument: Whether to save the argument for future runs

        Returns:
            The container ID of the launched agent
        """
        payload = {}

        if argument is not None:
            payload["argument"] = json.dumps(argument)

        if save_argument:
            payload["saveArgument"] = True

        result = await self._request_v1(
            "POST",
            f"/agent/{agent_id}/launch",
            json=payload if payload else None,
        )

        return result.get("containerId", "")

    async def get_agent_output(self, agent_id: str) -> AgentOutput:
        """Get the output of the most recent agent execution.

        Args:
            agent_id: The agent/phantom ID

        Returns:
            AgentOutput with execution results
        """
        result = await self._request_v2(
            "GET", f"/agents/fetch-output?id={agent_id}"
        )

        status = AgentStatus.FINISHED
        if result.get("status") == "running":
            status = AgentStatus.RUNNING
        elif result.get("status") == "error":
            status = AgentStatus.ERROR

        return AgentOutput(
            container_id=result.get("containerId", ""),
            status=status,
            result_object=result.get("resultObject"),
            output=result.get("output", ""),
            exit_code=result.get("exitCode"),
            error_message=result.get("error", ""),
        )

    async def wait_for_agent(
        self,
        agent_id: str,
        timeout_seconds: int = 300,
        poll_interval: int = 10,
    ) -> AgentOutput:
        """Wait for an agent to finish execution.

        Args:
            agent_id: The agent/phantom ID
            timeout_seconds: Maximum time to wait
            poll_interval: Seconds between status checks

        Returns:
            AgentOutput with final execution results

        Raises:
            TimeoutError: If agent doesn't finish within timeout
        """
        start_time = datetime.now()

        while True:
            output = await self.get_agent_output(agent_id)

            if output.status != AgentStatus.RUNNING:
                return output

            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout_seconds:
                raise TimeoutError(
                    f"Agent {agent_id} did not finish within {timeout_seconds}s"
                )

            await asyncio.sleep(poll_interval)

    async def launch_and_wait(
        self,
        agent_id: str,
        argument: Optional[dict] = None,
        timeout_seconds: int = 300,
    ) -> AgentOutput:
        """Launch an agent and wait for it to finish.

        Args:
            agent_id: The agent/phantom ID to launch
            argument: Optional JSON arguments to pass
            timeout_seconds: Maximum time to wait

        Returns:
            AgentOutput with execution results
        """
        await self.launch_agent(agent_id, argument)
        return await self.wait_for_agent(agent_id, timeout_seconds)

    async def scrape_linkedin_profile(
        self,
        agent_id: str,
        linkedin_url: str,
    ) -> LinkedInProfile:
        """Scrape a LinkedIn profile using a configured phantom.

        Args:
            agent_id: The LinkedIn Profile Scraper phantom ID
            linkedin_url: URL of the LinkedIn profile to scrape

        Returns:
            LinkedInProfile with scraped data
        """
        output = await self.launch_and_wait(
            agent_id,
            argument={"profileUrl": linkedin_url},
        )

        if output.status == AgentStatus.ERROR:
            raise Exception(f"Profile scrape failed: {output.error_message}")

        result = output.result_object or {}

        return LinkedInProfile(
            linkedin_url=linkedin_url,
            first_name=result.get("firstName", ""),
            last_name=result.get("lastName", ""),
            company=result.get("company", ""),
            position=result.get("jobTitle", result.get("title", "")),
            headline=result.get("headline", ""),
            location=result.get("location", ""),
            profile_picture_url=result.get("imgUrl", ""),
            connection_degree=result.get("connectionDegree", ""),
            summary=result.get("summary", ""),
        )

    async def send_linkedin_message(
        self,
        agent_id: str,
        linkedin_url: str,
        message: str,
    ) -> bool:
        """Send a LinkedIn message using a configured phantom.

        Args:
            agent_id: The LinkedIn Message Sender phantom ID
            linkedin_url: URL of the LinkedIn profile to message
            message: The message content to send

        Returns:
            True if message was sent successfully
        """
        output = await self.launch_and_wait(
            agent_id,
            argument={
                "profileUrl": linkedin_url,
                "message": message,
            },
        )

        if output.status == AgentStatus.ERROR:
            raise Exception(f"Message send failed: {output.error_message}")

        return True

    async def get_all_agents(self) -> list[dict]:
        """Get all agents in the organization.

        Returns:
            List of agent dictionaries
        """
        result = await self._request_v2("GET", "/agents/fetch-all")
        return result if isinstance(result, list) else []

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
