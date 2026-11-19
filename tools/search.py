
from ddgs import DDGS

from config import MAX_SEARCH_RESULTS


def search_company(query: str) -> dict:
    """Search the web for public company information."""

    print(f"🔎 TOOL CALLED: search_company({query})")

    try:
        results = DDGS().text(
            query,
            max_results=MAX_SEARCH_RESULTS
        )

        return {
            "query": query,
            "results": [
                {
                    "title": item.get("title"),
                    "url": item.get("href"),
                    "snippet": item.get("body"),
                }
                for item in results
            ],
        }

    except Exception as error:
        print(f"❌ Search failed: {error}")

        return {
            "error": str(error)
        }
