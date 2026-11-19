
import logging

from ddgs import DDGS

from config import MAX_SEARCH_RESULTS

from .budget import take_search

logger = logging.getLogger(__name__)

MAX_QUERY_CHARS = 200


def search_company(query: str) -> dict:
    """Search the web for public company information."""

    query = str(query or "").strip()[:MAX_QUERY_CHARS]
    logger.info("search_company(%r)", query)

    if not query:
        return {"error": "Empty search query."}

    if not take_search():
        return {"error": "Search budget exhausted."}

    try:
        results = DDGS().text(
            query,
            max_results=MAX_SEARCH_RESULTS
        ) or []

        return {
            "query": query,
            "results": [
                {
                    "title": item.get("title"),
                    "url": item.get("href"),
                    "snippet": item.get("body"),
                }
                for item in results
                if isinstance(item, dict)
            ],
        }

    except Exception as error:
        logger.warning("Search failed: %s", error)
        return {"error": "Search failed."}
