from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import FilterChain

class Crawler: 
    def __init__(self, url, max_depth=5):
        self.config = CrawlerRunConfig(
            deep_crawl_strategy=BFSDeepCrawlStrategy(
                max_depth=max_depth,
                filter_chain=FilterChain([])
            )
        )
        self.url = url
        
    async def crawl(self, url: str):
        all_content = ""
        async with AsyncWebCrawler() as crawler:
            results = await crawler.arun(url, config=self.config)

            for result in results:
                if hasattr(result, 'markdown') and result.markdown:
                    all_content += f"\n\n--- From : {getattr(result, 'url', 'Unknown')} ---\n"
                    all_content += result.markdown
                    
        return all_content
