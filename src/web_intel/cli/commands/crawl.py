import asyncio
from pathlib import Path
from typing import Optional

import typer
from typer import Typer

from web_intel.cli.ui.console import console
from web_intel.core.config import Config
from web_intel.crawlers.base import BaseCrawler
from web_intel.crawlers.factory import CrawlerFactory
from web_intel.models.crawl_result import CrawlResult
from web_intel.storage.base import BaseStorage
from web_intel.storage.factory import StorageFactory
from web_intel.utils.exceptions import CrawlerError, StorageError

app: Typer = typer.Typer(help="Crawl websites")


@app.command("url")
def crawl_url(
    url: str = typer.Argument(..., help="URL to crawl"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    depth: int = typer.Option(1, "--depth", "-d", help="Crawl depth"),
) -> None:
    """
    Crawl a single URL

    Examples:
        wi crawl url "https://example.com" -o data/example.md
        wi crawl url "https://example.com" -o data/example.md -d 5
    """
    asyncio.run(_crawl_url(url, output, depth))


async def _crawl_url(
    url: str = typer.Argument(..., help="URL to crawl"),
    output: Optional[Path] = typer.Option(None, "--output", "-o"),
    depth: int = typer.Option(1, "--depth", "-d"),
) -> None:
    try:
        """Async implementatl of crawl_url"""
        config: Config = Config()

        crawler: BaseCrawler = CrawlerFactory.create("crawl4ai", config)
        storage: BaseStorage = StorageFactory.create("file", config)

        crawl_res: CrawlResult = await crawler.crawl(url)

        saved_crawl_result_res: str = await storage.save_crawl_result(
            result=crawl_res, format="json"
        )

        print(f"Crawl Response {crawl_res}")
        print(f"Storage Response {saved_crawl_result_res}")

    except StorageError as e:
        console.print(f"[red]Storage error: [/red] {e}")
        raise typer.Exit(1)
    except CrawlerError as e:
        console.print(f"[red]Crawler error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        console.print_exception()
        raise typer.Exit(1)
