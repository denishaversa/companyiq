
def create_research_plan(company_name: str) -> str:
    """Create an end-to-end company research brief."""

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

RESEARCH INSTRUCTIONS:
- Search for reliable public sources.
- Prioritize official company information.
- Read relevant accessible webpages.
- Cite the exact URLs of retrieved sources.
- Distinguish verified facts from reasonable inferences.
- Do not invent internal processes, financial data,
  technology stacks, or KPIs.
- Explain gaps where information is unavailable.
- Respect the available research budget.
"""
