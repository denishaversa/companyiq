import re

import streamlit as st

from agent import research_company, summarize_report
from research.layout import focus_to_markdown, snapshot_to_markdown, split_focus
from research.pdf_export import report_to_pdf
from report_view import show_report

st.set_page_config(
    page_title="CompanyIQ",
    page_icon="🔍",
    layout="wide",
)

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
)

focus_team = st.text_input(
    "Which team or department do you want to know more about? (optional)",
    placeholder="e.g. Marketing, Customer Success, Data Engineering",
    help=(
        "Add the team you work in or are joining, and the report gets "
        "an extra section about that team at this company."
    ),
    max_chars=80,
)

if st.button("Research Company", type="primary"):

    if not company_name.strip():
        st.warning("Please enter a company name.")

    else:
        with st.spinner(
            f"Researching {company_name}..."
        ):
            try:
                report = research_company(
                    company_name.strip(),
                    focus_team.strip() or None,
                )

                st.session_state["report"] = report
                st.session_state["company"] = company_name.strip()
                st.session_state["focus_team"] = focus_team.strip()
                st.session_state["snapshot"] = summarize_report(
                    company_name.strip(), report
                )

            except Exception as error:
                st.error(f"Research failed: {error}")

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
    except Exception as error:
        st.error(f"Could not build the PDF: {error}")
    else:
        st.download_button(
            "Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"companyiq_{company_slug}_report.pdf",
            mime="application/pdf",
        )
