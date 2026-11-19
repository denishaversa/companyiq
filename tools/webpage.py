
import ipaddress
import logging
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import (
    MAX_WEBPAGE_BYTES,
    MAX_WEBPAGE_CHARACTERS,
    REQUEST_TIMEOUT,
)

from .budget import take_webpage

logger = logging.getLogger(__name__)


def is_safe_url(url: str) -> bool:
    """Allow HTTPS URLs with public network destinations."""

    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError:
        return False

    if port not in (None, 443):
        return False

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


def read_webpage(url: str) -> dict:
    """Read text from a public HTML webpage.

    Args:
        url: The HTTPS URL of a public HTML webpage.
    """

    url = str(url or "").strip()
    logger.info("read_webpage(%r)", url[:300])

    if not is_safe_url(url):
        return {"error": "URL is not allowed."}

    if urlparse(url).path.lower().endswith(".pdf"):
        return {"error": "PDF reading is not supported yet."}

    if not take_webpage():
        return {"error": "Webpage budget exhausted."}

    try:
        # Disable redirects until we add redirect validation.
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
            headers={"User-Agent": "CompanyIQ/0.1"},
            stream=True,
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

        # Read at most MAX_WEBPAGE_BYTES, so a huge page can't use up memory.
        body = b""
        for chunk in response.iter_content(chunk_size=65536):
            body += chunk
            if len(body) >= MAX_WEBPAGE_BYTES:
                body = body[:MAX_WEBPAGE_BYTES]
                break
        response.close()

        soup = BeautifulSoup(
            body,
            "html.parser",
            from_encoding=response.encoding,
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


        return {
            "url": response.url,
            "title": title,
            "content": content[:MAX_WEBPAGE_CHARACTERS],
        }

    except requests.RequestException as error:
        logger.warning("Webpage retrieval failed: %s", error)
        return {"error": "Could not read this webpage."}
