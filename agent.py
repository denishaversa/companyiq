
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
