
import streamlit as st

from agent import research_company

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

    st.download_button(
        "Download Report",
        data=st.session_state["report"],
        file_name="companyiq_report.md",
        mime="text/markdown",
    )
