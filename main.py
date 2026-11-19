
from agent import ResearchError, research_company
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

    focus_team = input(
        "Which team or department do you want to know more about? "
        "(optional, press Enter to skip) "
    ).strip()

    try:
        report = research_company(company_name, focus_team or None)
    except ResearchError as error:
        print(error)
        return

    display_report(company_name, report)


if __name__ == "__main__":
    main()
