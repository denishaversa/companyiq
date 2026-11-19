"""Per-report research budget.

Each report gets its own budget, so visitors using the app at the same time
don't share (or use up) each other's webpage and search allowance.
"""

from contextvars import ContextVar
from dataclasses import dataclass

from config import MAX_SEARCH_CALLS, MAX_WEBPAGE_CALLS


@dataclass
class Budget:
    webpages_left: int = MAX_WEBPAGE_CALLS
    searches_left: int = MAX_SEARCH_CALLS


# With no budget started, nothing is allowed.
_budget: ContextVar[Budget] = ContextVar(
    "research_budget", default=Budget(webpages_left=0, searches_left=0)
)


def start_budget() -> None:
    """Give the current report a fresh budget."""

    _budget.set(Budget())


def take_webpage() -> bool:
    budget = _budget.get()
    if budget.webpages_left <= 0:
        return False
    budget.webpages_left -= 1
    return True


def take_search() -> bool:
    budget = _budget.get()
    if budget.searches_left <= 0:
        return False
    budget.searches_left -= 1
    return True
