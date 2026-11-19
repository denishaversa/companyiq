"""Clean and check what visitors type before it reaches the model."""

import re
import unicodedata

from config import MAX_COMPANY_NAME_CHARS, MAX_FOCUS_TEAM_CHARS

_SPACES_RE = re.compile(r"\s+")


def clean_text(value: str | None, max_chars: int) -> str:
    """Drop control and invisible characters, squeeze spaces, cap length."""

    if not value:
        return ""

    kept = "".join(
        " " if ch.isspace() else ch
        for ch in str(value)
        if ch.isspace() or not unicodedata.category(ch).startswith("C")
    )

    return _SPACES_RE.sub(" ", kept).strip()[:max_chars].strip()


def check_company_name(value: str | None) -> tuple[str, str | None]:
    """Return (cleaned name, problem message or None)."""

    name = clean_text(value, MAX_COMPANY_NAME_CHARS)

    if not name:
        return "", "Please enter a company name."

    if not any(ch.isalnum() for ch in name):
        return "", "Please enter a company name using letters or numbers."

    return name, None


def check_focus_team(value: str | None) -> str | None:
    """Return the cleaned team name, or None when it was left empty."""

    team = clean_text(value, MAX_FOCUS_TEAM_CHARS)

    if not any(ch.isalnum() for ch in team):
        return None

    return team


def cache_key(value: str | None) -> str:
    """The same company typed in different ways shares one cached report."""

    return (value or "").casefold()
