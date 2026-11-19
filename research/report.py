
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

console = Console()


def display_report(company_name: str, report: str):
    """Display a formatted CompanyIQ research report."""

    console.print()

    console.print(
        Panel(
            f"[bold]CompanyIQ Research: {company_name}[/bold]",
            title="🔍 CompanyIQ",
            border_style="blue",
        )
    )

    console.print(Markdown(report))

    console.print(
        "\n[dim]End of CompanyIQ Report[/dim]\n"
    )
