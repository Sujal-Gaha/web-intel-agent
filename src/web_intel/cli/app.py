import typer
from typer import Typer

from web_intel.cli.commands import crawl, query
from web_intel.cli.ui.console import console

app: Typer = typer.Typer(
    name="wi",
    help="🕷️ Intelligent web crawling and AI-powered querying",
    add_completion=False,
)

# Register command groups
app.add_typer(crawl.app, name="crawl")
app.add_typer(query.app, name="query")

# Register config command group here later


@app.command()
def version() -> None:
    """Show version information."""
    console.print("web-intel version 0.1.0", style="bold green")


@app.callback()
def callback() -> None:
    """
    Web Intel - Crawl websites and query content with AI.
    """
    pass
