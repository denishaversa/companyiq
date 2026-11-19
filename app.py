import logging
import re
import threading
import time
from collections import deque

import streamlit as st

from agent import ResearchError, research_company, summarize_report
from config import (
    CACHE_TTL_SECONDS,
    MAX_COMPANY_NAME_CHARS,
    MAX_FOCUS_TEAM_CHARS,
    MAX_NEW_REPORTS_PER_HOUR,
    MAX_RUNS_PER_SESSION,
    SESSION_COOLDOWN_SECONDS,
    get_gemini_api_key,
)
from research.inputs import cache_key, check_company_name, check_focus_team
from research.layout import focus_to_markdown, snapshot_to_markdown, split_focus
from research.pdf_export import report_to_pdf
from report_view import show_report

st.set_page_config(
    page_title="CompanyIQ",
    page_icon="🔍",
    layout="wide",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


class HourlyLimit:
    """Counts new reports across all visitors, to protect the API quota."""

    def __init__(self, max_per_hour: int):
        self.max_per_hour = max_per_hour
        self.started = deque()
        self.lock = threading.Lock()

    def try_start(self) -> bool:
        now = time.time()
        with self.lock:
            while self.started and now - self.started[0] > 3600:
                self.started.popleft()
            if len(self.started) >= self.max_per_hour:
                return False
            self.started.append(now)
            return True


@st.cache_resource
def hourly_limit() -> HourlyLimit:
    # One shared counter for the whole app (all visitors).
    return HourlyLimit(MAX_NEW_REPORTS_PER_HOUR)


@st.cache_data(ttl=CACHE_TTL_SECONDS, max_entries=200, show_spinner=False)
def cached_research(
    company_key: str, focus_key: str, _company: str, _focus: str | None
) -> tuple[str, dict | None]:
    """Research a company, reusing a recent report for the same request.

    Only company_key and focus_key decide what is reused (the underscore
    arguments are ignored by the cache). Errors are not cached, so a
    failed run can simply be tried again.
    """

    if not hourly_limit().try_start():
        raise ResearchError(
            "CompanyIQ has had a lot of requests in the last hour. "
            "Please try again a little later."
        )

    report = research_company(_company, _focus)
    snapshot = summarize_report(_company, report)
    return report, snapshot


def session_wait_message() -> str | None:
    """Per-visitor limits: a short pause between runs, and a cap per visit."""

    runs = st.session_state.get("run_times", [])

    if len(runs) >= MAX_RUNS_PER_SESSION:
        return (
            "You've reached the number of reports for this visit. "
            "Please come back later."
        )

    if runs:
        wait = SESSION_COOLDOWN_SECONDS - (time.time() - runs[-1])
        if wait > 0:
            return f"Please wait {int(wait) + 1} seconds before the next report."

    return None


st.title("🔍 CompanyIQ")
st.subheader("Understand any company.")

st.write(
    "Your AI-powered business research assistant. "
    "Explore business models, products, revenue, "
    "customers, and competitive advantages."
)

company_name = st.text_input(
    "Which company would you like to research?",
    placeholder="e.g. Stripe, Datadog, NVIDIA",
    max_chars=MAX_COMPANY_NAME_CHARS,
)

focus_team = st.text_input(
    "Which team or department do you want to know more about? (optional)",
    placeholder="e.g. Marketing, Customer Success, Data Engineering",
    help=(
        "Add the team you work in or are joining, and the report gets "
        "an extra section about that team at this company."
    ),
    max_chars=MAX_FOCUS_TEAM_CHARS,
)

if not get_gemini_api_key():
    st.error(
        "CompanyIQ isn't set up yet: the Gemini API key is missing. "
        "If you run this app, add GEMINI_API_KEY to its secrets."
    )
    st.stop()

if st.button("Research Company", type="primary"):

    company, problem = check_company_name(company_name)
    team = check_focus_team(focus_team)
    wait_message = None if problem else session_wait_message()

    if problem:
        st.warning(problem)

    elif wait_message:
        st.info(wait_message)

    else:
        st.session_state.setdefault("run_times", []).append(time.time())

        with st.spinner(
            f"Researching {company}... this can take a minute."
        ):
            try:
                report, snapshot = cached_research(
                    cache_key(company), cache_key(team), company, team
                )

            except ResearchError as error:
                st.error(str(error))

            except Exception:
                logging.getLogger(__name__).exception("Unexpected error")
                st.error(
                    "Something went wrong while researching. "
                    "Please try again."
                )

            else:
                st.session_state["report"] = report
                st.session_state["company"] = company
                st.session_state["focus_team"] = team or ""
                st.session_state["snapshot"] = snapshot

if "report" in st.session_state:
    st.divider()

    st.header(
        f"Company Research: {st.session_state['company']}"
    )

    snapshot = st.session_state.get("snapshot")

    focus_team_shown = st.session_state.get("focus_team") or None

    show_report(st.session_state["report"], snapshot, focus_team_shown)

    company_slug = re.sub(
        r"[^A-Za-z0-9]+", "_", st.session_state["company"]
    ).strip("_").lower() or "company"

    try:
        # The PDF always holds the whole report, every section in full,
        # whatever is open or closed on screen.
        # The team focus section goes right after the snapshot, as on screen.
        focus_section, rest_of_report = (
            split_focus(st.session_state["report"])
            if focus_team_shown
            else (None, st.session_state["report"])
        )
        pdf_markdown = "\n\n".join(
            part for part in (
                snapshot_to_markdown(snapshot),
                focus_to_markdown(focus_section),
                rest_of_report,
            ) if part
        )
        pdf_bytes = report_to_pdf(
            st.session_state["company"],
            pdf_markdown,
        )
    except Exception:
        logging.getLogger(__name__).exception("PDF export failed")
        st.error("Sorry, the PDF couldn't be built for this report.")
    else:
        st.download_button(
            "Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"companyiq_{company_slug}_report.pdf",
            mime="application/pdf",
        )
