import asyncio
from datetime import datetime
from typing import Callable, Iterable, Optional
from urllib.parse import ParseResult, urlparse

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import FilterChain

from web_intel.core.config import Config
from web_intel.crawlers.base import BaseCrawler
from web_intel.models.crawl_result import CrawlResult, PageResult
from web_intel.utils.exceptions import CrawlerError


class Crawl4AICrawler(BaseCrawler):
    """Crawl4AI-based web crawler implementation."""

    def __init__(
        self,
        config: Config,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> None:
        """Initialize Crawl4AI crawler."""
        self.config: Config = config
        self.progress_callback = progress_callback
        self.timeout: int = config.crawler_timeout

    async def validate_url(self, url: str) -> bool:
        """Validate URL format and accessibility."""
        try:
            parsed: ParseResult = urlparse(url)
            if parsed.scheme not in ["http", "https"]:
                return False
            if not parsed.netloc:
                return False
            return True
        except Exception:
            return False

    async def crawl(
        self,
        url: str,
        depth: int = 5,
        max_pages: Optional[int] = None,
        filter_chain: Optional[FilterChain] = None,
        verbose: bool = False,
        **options,
    ) -> CrawlResult:
        """Crawl a URL using Crawl4AI."""
        start_time = datetime.now()

        if not await self.validate_url(url):
            raise CrawlerError(f"Invalid URL: {url}")

        try:
            crawler_config = self._build_config(
                depth=depth, filter_chain=filter_chain or FilterChain([]), **options
            )

            pages: list[PageResult] = []
            failed_count = 0

            if self.progress_callback:
                self.progress_callback("Starting crawl...", 0, 0)

            async with AsyncWebCrawler(verbose=verbose) as crawler:
                try:
                    results = await crawler.arun(url, config=crawler_config)

                    if not isinstance(results, Iterable):
                        raise CrawlerError("Crawl results are not iterable")

                    async def process_with_timeout() -> None:
                        nonlocal failed_count
                        idx = 0
                        for result in results:
                            idx += 1
                            try:
                                if self.progress_callback:
                                    self.progress_callback(
                                        f"Processing page {idx}...",
                                        idx,
                                        0,
                                    )

                                page: PageResult = self._extract_page_result(result)
                                pages.append(page)

                                if max_pages and len(pages) >= max_pages:
                                    break

                            except Exception as e:
                                failed_count += 1
                                if verbose:
                                    print(f"Failed to process page: {e}")
                                continue

                    await asyncio.wait_for(
                        process_with_timeout(), timeout=self.timeout * depth
                    )

                except asyncio.TimeoutError:
                    raise CrawlerError(
                        f"Crawl timed out after {self.timeout * depth} seconds"
                    )

            end_time: datetime = datetime.now()

            return CrawlResult(
                source_url=url,
                pages=pages,
                success=len(pages) > 0,
                total_pages=len(pages),
                failed_pages=failed_count,
                crawl_depth=depth,
                started_at=start_time,
                completed_at=end_time,
                metadata={
                    "crawler": "crawl4ai",
                    "duration_seconds": (end_time - start_time).total_seconds(),
                    "max_pages": max_pages,
                },
            )

        except CrawlerError:
            raise
        except Exception as e:
            raise CrawlerError(f"Crawl failed: {str(e)}") from e

    def _build_config(
        self, depth: int, filter_chain: FilterChain, **options
    ) -> CrawlerRunConfig:
        """Build Crawl4AI configuration."""
        strategy: BFSDeepCrawlStrategy = BFSDeepCrawlStrategy(
            max_depth=depth, filter_chain=filter_chain
        )

        return CrawlerRunConfig(deep_crawl_strategy=strategy, **options)

    def _extract_page_result(self, result) -> PageResult:
        """Extract PageResult from Crawl4AI result."""
        # Extract URL
        url = getattr(result, "url", "Unknown")

        # Extract content (prefer markdown)
        content = ""
        if hasattr(result, "markdown") and result.markdown:
            content = result.markdown
        elif hasattr(result, "cleaned_html"):
            content = result.cleaned_html
        elif hasattr(result, "html"):
            content = result.html

        if not content:
            raise ValueError(f"No content extracted from {url}")

        # Extract metadata
        title = getattr(result, "title", None)
        status_code = getattr(result, "status_code", None)

        return PageResult(
            url=url,
            content=content,
            title=title,
            status_code=status_code,
            metadata={
                "has_markdown": hasattr(result, "markdown"),
                "content_length": len(content),
            },
        )
