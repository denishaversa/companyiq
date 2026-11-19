import re

import streamlit as st

from agent import research_company
from research.pdf_export import report_to_pdf

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

if st.button("Research Company", type="primary"):

    if not company_name.strip():
        st.warning("Please enter a company name.")

    else:
        with st.spinner(
            f"Researching {company_name}..."
        ):
            try:
                report = research_company(
                    company_name.strip()
                )

                st.session_state["report"] = report
                st.session_state["company"] = company_name.strip()

            except Exception as error:
                st.error(f"Research failed: {error}")

if "report" in st.session_state:
    st.divider()

    st.header(
        f"Company Research: {st.session_state['company']}"
    )

    st.markdown(st.session_state["report"])

    company_slug = re.sub(
        r"[^A-Za-z0-9]+", "_", st.session_state["company"]
    ).strip("_").lower() or "company"

    try:
        pdf_bytes = report_to_pdf(
            st.session_state["company"],
            st.session_state["report"],
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
