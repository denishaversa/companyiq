
def get_company_info(company_name: str) -> dict:
    """Retrieve sample company information from local data."""

    companies = {
        "datadog": {
            "name": "Datadog",
            "business_model": "SaaS with usage-based pricing",
            "products": [
                "Infrastructure Monitoring",
                "Application Performance Monitoring",
                "Log Management",
            ],
        },
        "stripe": {
            "name": "Stripe",
            "business_model": "Payments and financial infrastructure",
            "products": [
                "Payments",
                "Billing",
                "Connect",
            ],
        },
    }

    return companies.get(
        str(company_name or "").strip().lower(),
        {"error": f"No local information for {company_name}"}
    )
