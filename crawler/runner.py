from pathlib import Path
from crawler.crawler import Crawler

async def run_crawler(url: str, output_file: str):
    """Run the crawler and save the result."""
    print(f"Starting crawl for: {url}")
    crawler = Crawler(url, max_depth=100)
    content = await crawler.crawl()

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Crawling finished. Content saved to {output_path}")
    return output_path
