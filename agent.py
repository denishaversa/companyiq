import json

from google import genai
from google.genai import types, errors

from config import GEMINI_API_KEY, MODEL_NAME
from tools import (
    get_company_info,
    search_company,
    read_webpage,
    reset_webpage_budget,
)
from research import create_research_plan


client = genai.Client(api_key=GEMINI_API_KEY)


def research_company(company_name: str) -> str:
    """Run a CompanyIQ research session."""

    reset_webpage_budget()

    chat = client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            tools=[
                get_company_info,
                search_company,
                read_webpage,
            ],
            temperature=0,
            system_instruction=(
                "You are CompanyIQ, a business research "
                "assistant. Prioritize official sources, "
                "verify claims using retrieved evidence, "
                "and distinguish facts from interpretations."
            ),
        ),
    )

    research_plan = create_research_plan(company_name)

    try:
        response = chat.send_message(research_plan)

        if not response.text:
            return "No report was generated."

        return response.text

    except errors.ServerError as error:
        if error.code == 503:
            return (
                "Gemini is temporarily unavailable. "
                "Please try again later."
            )

        raise


SNAPSHOT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "summary": {"type": "STRING"},
        "industry": {"type": "STRING"},
        "founded": {"type": "STRING"},
        "headquarters": {"type": "STRING"},
        "revenue_model": {"type": "STRING"},
        "competitors": {"type": "ARRAY", "items": {"type": "STRING"}},
        "risks": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "level": {
                        "type": "STRING",
                        "enum": ["High", "Medium", "Low"],
                    },
                    "risk": {"type": "STRING"},
                },
                "required": ["level", "risk"],
            },
        },
        "process_steps": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "step": {"type": "STRING"},
                    "detail": {"type": "STRING"},
                },
                "required": ["step", "detail"],
            },
        },
    },
    "required": [
        "summary", "industry", "founded", "headquarters",
        "revenue_model", "competitors", "risks", "process_steps",
    ],
}


def summarize_report(company_name: str, report: str) -> dict | None:
    """Pull the at-a-glance facts out of a finished report.

    Uses only the report text, so nothing new is researched. Returns None
    if the facts can't be produced; the app then shows the report without
    the snapshot.
    """

    prompt = f"""
Read this research report about {company_name} and fill in the fields.

Rules:
- Use only information stated in the report. Do not add anything.
- If the report does not state a fact, write "Not stated".
- summary: one or two plain sentences on what the company does and
  how it makes money.
- industry, founded, headquarters, revenue_model: a few words each.
- competitors: up to 6 company names.
- risks: up to 4 of the biggest risks, each one short sentence, with
  a level of High, Medium or Low.
- process_steps: 4 to 6 stages of how the business runs, in order.
  step is 2 to 4 words; detail is a few words.

REPORT:
{report}
"""

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                response_mime_type="application/json",
                response_schema=SNAPSHOT_SCHEMA,
            ),
        )
        snapshot = response.parsed
        if snapshot is None and response.text:
            snapshot = json.loads(response.text)
    except Exception:
        return None

    if not isinstance(snapshot, dict):
        return None

    return snapshot
