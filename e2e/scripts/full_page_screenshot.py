#!/usr/bin/env python3
"""
Full-page screenshot capture utility.

This script captures a full-page screenshot of a web page without requiring
multiple scroll-and-stitch operations, saving time and tokens when used with Claude.

Usage:
    python full_page_screenshot.py <url> <output_path>

Example:
    python full_page_screenshot.py https://example.com screenshot.png
"""

import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def capture_full_page(url: str, output_path: str, wait_seconds: int = 2) -> str:
    """
    Capture a full-page screenshot of the given URL.

    Args:
        url: The URL to capture
        output_path: Where to save the screenshot
        wait_seconds: Time to wait for page to load (default 2s)

    Returns:
        The path to the saved screenshot
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)

        # Wait for page to load
        time.sleep(wait_seconds)

        # Calculate full page dimensions
        width = driver.execute_script(
            "return Math.max(document.body.scrollWidth, "
            "document.documentElement.scrollWidth, "
            "document.body.offsetWidth, "
            "document.documentElement.offsetWidth, "
            "document.body.clientWidth, "
            "document.documentElement.clientWidth);"
        )
        height = driver.execute_script(
            "return Math.max(document.body.scrollHeight, "
            "document.documentElement.scrollHeight, "
            "document.body.offsetHeight, "
            "document.documentElement.offsetHeight, "
            "document.body.clientHeight, "
            "document.documentElement.clientHeight);"
        )

        # Set window size to full page dimensions (with reasonable limits)
        max_height = 10000  # Prevent extremely tall screenshots
        height = min(height, max_height)
        driver.set_window_size(width, height)

        # Small delay after resize
        time.sleep(0.5)

        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Capture screenshot
        driver.save_screenshot(output_path)
        print(f"Captured full page screenshot: {output_path}")
        print(f"Dimensions: {width}x{height}")

        return output_path

    finally:
        driver.quit()


def capture_viewport(url: str, output_path: str, width: int = 1920, height: int = 1080) -> str:
    """
    Capture a viewport-sized screenshot (above the fold only).

    Args:
        url: The URL to capture
        output_path: Where to save the screenshot
        width: Viewport width (default 1920)
        height: Viewport height (default 1080)

    Returns:
        The path to the saved screenshot
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"--window-size={width},{height}")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(2)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(output_path)

        print(f"Captured viewport screenshot: {output_path}")
        print(f"Dimensions: {width}x{height}")

        return output_path

    finally:
        driver.quit()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python full_page_screenshot.py <url> <output_path> [--viewport]")
        print("  --viewport: Capture only the visible viewport instead of full page")
        sys.exit(1)

    url = sys.argv[1]
    output_path = sys.argv[2]
    viewport_only = "--viewport" in sys.argv

    if viewport_only:
        capture_viewport(url, output_path)
    else:
        capture_full_page(url, output_path)
