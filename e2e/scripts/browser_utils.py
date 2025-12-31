#!/usr/bin/env python3
"""
Browser utilities for E2E testing with Claude.

This module provides helper functions for browser automation tasks
that can be called from Claude or test scripts.
"""

import json
import time
from pathlib import Path
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BrowserHelper:
    """Helper class for browser automation tasks."""

    def __init__(self, headless: bool = True):
        """Initialize browser helper.

        Args:
            headless: Run browser in headless mode (default True)
        """
        self.headless = headless
        self.driver = None
        self._scripts_dir = Path(__file__).parent

    def start(self) -> webdriver.Chrome:
        """Start the browser."""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver

    def stop(self):
        """Stop the browser."""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def navigate(self, url: str, wait_seconds: float = 2.0):
        """Navigate to a URL and wait for page load.

        Args:
            url: The URL to navigate to
            wait_seconds: Time to wait after navigation
        """
        if not self.driver:
            self.start()
        self.driver.get(url)
        time.sleep(wait_seconds)

    def dismiss_banners(self) -> int:
        """Inject and execute the banner dismissal script.

        Returns:
            Number of elements dismissed
        """
        script_path = self._scripts_dir / "auto_dismiss_banners.js"
        with open(script_path, "r") as f:
            script = f.read()

        result = self.driver.execute_script(script)
        return result or 0

    def full_page_screenshot(self, output_path: str) -> str:
        """Capture a full-page screenshot.

        Args:
            output_path: Where to save the screenshot

        Returns:
            Path to the saved screenshot
        """
        # Calculate full page dimensions
        width = self.driver.execute_script(
            "return Math.max(document.body.scrollWidth, "
            "document.documentElement.scrollWidth);"
        )
        height = self.driver.execute_script(
            "return Math.max(document.body.scrollHeight, "
            "document.documentElement.scrollHeight);"
        )

        # Limit height to prevent memory issues
        height = min(height, 10000)

        # Resize window
        self.driver.set_window_size(width, height)
        time.sleep(0.5)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Capture
        self.driver.save_screenshot(output_path)
        return output_path

    def get_console_logs(self) -> list:
        """Get browser console logs.

        Returns:
            List of console log entries
        """
        try:
            logs = self.driver.get_log("browser")
            return logs
        except Exception:
            return []

    def wait_for_element(
        self,
        selector: str,
        by: str = "css",
        timeout: int = 10
    ) -> Optional[object]:
        """Wait for an element to be present.

        Args:
            selector: The element selector
            by: Selector type ('css', 'xpath', 'id')
            timeout: Max wait time in seconds

        Returns:
            The element if found, None otherwise
        """
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME
        }

        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_map.get(by, By.CSS_SELECTOR), selector))
            )
            return element
        except TimeoutException:
            return None

    def click_element(self, selector: str, by: str = "css") -> bool:
        """Click an element.

        Args:
            selector: The element selector
            by: Selector type

        Returns:
            True if clicked successfully
        """
        element = self.wait_for_element(selector, by, timeout=5)
        if element:
            try:
                element.click()
                return True
            except Exception:
                pass
        return False

    def get_text(self, selector: str, by: str = "css") -> Optional[str]:
        """Get text content of an element.

        Args:
            selector: The element selector
            by: Selector type

        Returns:
            Text content or None
        """
        element = self.wait_for_element(selector, by, timeout=5)
        if element:
            return element.text
        return None

    def execute_script(self, script: str) -> any:
        """Execute JavaScript in the browser.

        Args:
            script: JavaScript code to execute

        Returns:
            Result of the script execution
        """
        return self.driver.execute_script(script)

    def get_page_info(self) -> dict:
        """Get information about the current page.

        Returns:
            Dictionary with page info
        """
        return {
            "url": self.driver.current_url,
            "title": self.driver.title,
            "width": self.driver.execute_script("return window.innerWidth"),
            "height": self.driver.execute_script("return window.innerHeight"),
            "scroll_height": self.driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
        }

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


if __name__ == "__main__":
    # Example usage
    with BrowserHelper(headless=True) as browser:
        browser.navigate("https://example.com")
        dismissed = browser.dismiss_banners()
        print(f"Dismissed {dismissed} banners")

        info = browser.get_page_info()
        print(f"Page: {info['title']} ({info['url']})")

        browser.full_page_screenshot("e2e/screenshots/example.png")
        print("Screenshot saved")
