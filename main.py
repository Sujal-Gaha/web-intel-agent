from crawler.crawler import Crawler
from ai_agent.ai_agent import AIAgent
import asyncio

OUTPUT_FILE = "./data/output.md"

async def main():
    url = input("Enter the website URL: ") or "https://www.sujalgahamagar.com.np"
    
    crawler = Crawler(url, max_depth=100)
    content = await crawler.crawl(url)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"\nCrawling finished. Content saved to {OUTPUT_FILE}")

    agent = AIAgent(file_path=OUTPUT_FILE)
    agent.process()


if __name__ == "__main__":
    asyncio.run(main())