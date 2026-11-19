
import ipaddress
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import (
    MAX_WEBPAGE_CALLS,
    MAX_WEBPAGE_CHARACTERS,
    REQUEST_TIMEOUT,
)


webpage_calls = 0


def is_safe_url(url: str) -> bool:
    """Allow HTTPS URLs with public network destinations."""

    parsed = urlparse(url)

    if parsed.scheme != "https":
        return False

    if not parsed.hostname:
        return False

    if parsed.username or parsed.password:
        return False

    try:
        addresses = socket.getaddrinfo(
            parsed.hostname,
            443,
            type=socket.SOCK_STREAM,
        )

        return bool(addresses) and all(
            ipaddress.ip_address(address[4][0]).is_global
            for address in addresses
        )

    except (OSError, ValueError):
        return False


def reset_webpage_budget():
    """Reset the webpage counter for a new research session."""

    global webpage_calls
    webpage_calls = 0


def read_webpage(url: str) -> dict:
    """Read text from a public HTML webpage.

    Args:
        url: The HTTPS URL of a public HTML webpage.
    """

    global webpage_calls

    print(f"🌐 TOOL CALLED: read_webpage({url})")

    if webpage_calls >= MAX_WEBPAGE_CALLS:
        return {"error": "Webpage budget exhausted."}

    if not is_safe_url(url):
        return {"error": "URL is not allowed."}

    if urlparse(url).path.lower().endswith(".pdf"):
        return {"error": "PDF reading is not supported yet."}

    webpage_calls += 1

    try:
        # Disable redirects until we add redirect validation.
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
            headers={"User-Agent": "CompanyIQ/0.1"},
        )

        if 300 <= response.status_code < 400:
            return {
                "error": "Redirect encountered; not followed."
            }

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if "text/html" not in content_type:
            return {"error": "URL did not return HTML."}

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for element in soup(
            ["script", "style", "nav", "footer"]
        ):
            element.decompose()

        title = (
            soup.title.get_text(strip=True)
            if soup.title else ""
        )

        content = soup.get_text(
            separator=" ",
            strip=True,
        )

        print("✅ Webpage retrieved successfully.")

        return {
            "url": response.url,
            "title": title,
            "content": content[:MAX_WEBPAGE_CHARACTERS],
        }

    except requests.RequestException as error:
        print(f"❌ Webpage retrieval failed: {error}")
        return {"error": str(error)}
