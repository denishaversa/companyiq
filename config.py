"""CompanyIQ settings.

The Gemini key is read from the GEMINI_API_KEY environment variable (or a
local .env file), and on Streamlit Community Cloud from the app's Secrets.
It is never stored in the code.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_gemini_api_key() -> str | None:
    """Return the Gemini API key, or None when it hasn't been set up."""

    key = os.environ.get("GEMINI_API_KEY", "")

    if not key.strip():
        try:
            import streamlit as st

            key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            # No secrets file, or not running inside Streamlit.
            key = ""

    return str(key).strip() or None


def _int_setting(name: str, default: int) -> int:
    """Read a whole-number setting from the environment, with a default."""

    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

# Research budget for one report.
MAX_WEBPAGE_CALLS = 3
MAX_SEARCH_CALLS = 6
MAX_TOOL_CALLS = 12
MAX_SEARCH_RESULTS = 5
MAX_WEBPAGE_CHARACTERS = 12000
MAX_WEBPAGE_BYTES = 2_000_000  # stop downloading a page after ~2 MB
REQUEST_TIMEOUT = 15

# What visitors can type.
MAX_COMPANY_NAME_CHARS = 100
MAX_FOCUS_TEAM_CHARS = 80

# The snapshot only needs the report, so very long reports are trimmed.
MAX_REPORT_CHARS_FOR_SNAPSHOT = 60000

# Protecting the Gemini quota on a public app.
# Finished reports are reused for the same company and team for a while.
CACHE_TTL_SECONDS = _int_setting("CACHE_TTL_SECONDS", 6 * 60 * 60)
# New (not cached) reports the whole app may start per hour, for all visitors.
MAX_NEW_REPORTS_PER_HOUR = _int_setting("MAX_NEW_REPORTS_PER_HOUR", 30)
# Per visitor (browser tab): wait between runs, and runs per visit.
SESSION_COOLDOWN_SECONDS = _int_setting("SESSION_COOLDOWN_SECONDS", 20)
MAX_RUNS_PER_SESSION = _int_setting("MAX_RUNS_PER_SESSION", 10)
