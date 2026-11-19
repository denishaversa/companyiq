
def _team_focus_section(focus_team: str) -> str:
    """Extra report section about one team or department."""

    return f"""
9. TEAM FOCUS: {focus_team.upper()}
Write this section for someone who works in, or is about to join,
the {focus_team} team (or the closest matching department) at this company.
Start this section's heading with the words "TEAM FOCUS".
- What this team does at this company and why it matters to the business
- How the team is organized and who leads it, if publicly known
- Where it sits in the end-to-end business process above, and which
  other teams it works with most closely
- Current priorities, projects, or initiatives that involve this team
- Tools, technology, and systems the team likely uses (say when this is
  inferred, for example from job postings)
- How the team's success is likely measured (KPIs)
- Recent news, hiring, or job posting signals about this team
- Challenges the team faces, and good questions to ask to learn more
If little is public about this team, say so plainly and explain what
can reasonably be inferred from the company's business model.
"""


def create_research_plan(company_name: str, focus_team: str | None = None) -> str:
    """Create an end-to-end company research brief.

    focus_team is an optional team or department (e.g. "Marketing") that
    gets its own section at the end of the report.
    """

    focus_team = (focus_team or "").strip()
    focus_section = _team_focus_section(focus_team) if focus_team else ""
    focus_instruction = (
        f"\n- Search specifically for information about the {focus_team} team\n"
        f"  (careers pages, job postings, team or engineering blogs, news)."
        if focus_team else ""
    )

    return f"""
You are CompanyIQ, a business intelligence research agent.

Research company: {company_name}

Produce a comprehensive analysis with these sections:

1. COMPANY OVERVIEW
- What does the company do?
- What problems does it solve?
- What markets does it serve?

2. BUSINESS MODEL
- How does the company create value?
- How does it capture value?
- What are its revenue streams?

3. PRODUCTS AND SERVICES
- What are its major products?
- Who uses and pays for each product?

4. END-TO-END BUSINESS PROCESS
Explain the company's operating lifecycle:
- Market research and strategy
- Product development and sourcing
- Marketing and customer acquisition
- Sales and customer onboarding
- Product or service delivery
- Payment, billing, and revenue collection
- Customer support and retention
- Analytics, optimization, and scaling

For each stage, explain:
- Activities and workflows
- Teams and stakeholders involved
- Technology and systems used, if known
- Business value created
- Relevant operational KPIs

5. VALUE CHAIN AND DEPENDENCIES
- Key suppliers and partners
- Distribution channels
- Important operational dependencies

6. COMPETITIVE LANDSCAPE
- Main competitors
- Differentiation and competitive advantages

7. FINANCIAL AND OPERATIONAL ECONOMICS
- Revenue drivers
- Major cost drivers
- Unit economics where publicly available
- Key business metrics

8. STRATEGY AND RISKS
- Growth strategy
- Operational bottlenecks
- Major business risks
{focus_section}
RESEARCH INSTRUCTIONS:
- Search for reliable public sources.
- Prioritize official company information.
- Read relevant accessible webpages.
- Cite the exact URLs of retrieved sources.
- Distinguish verified facts from reasonable inferences.
- Do not invent internal processes, financial data,
  technology stacks, or KPIs.
- Explain gaps where information is unavailable.
- Respect the available research budget.{focus_instruction}
"""
