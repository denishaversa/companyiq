
from agent import research_company
from research import display_report


def main():
    print("\n🔍 Welcome to CompanyIQ!")
    print("Your AI-powered company research assistant.\n")

    company_name = input(
        "Which company would you like to research? "
    ).strip()

    if not company_name:
        print("Please enter a company name.")
        return

    report = research_company(company_name)

    display_report(company_name, report)


if __name__ == "__main__":
    main()
