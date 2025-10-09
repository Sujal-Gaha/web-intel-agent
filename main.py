import argparse
import asyncio
from ai_agent_v0 import run_ai_agent
from crawler import run_crawler

CRAWLER_OUTPUT_FILE = "data/output.md"
AI_OUTPUT_FILE = "data/output.json"
DEFAULT_URL = "https://www.sujalgahamagar.com.np"

async def main():
    parser = argparse.ArgumentParser(
        description="CLI for Crawler and AI Agent processing."
    )

    subparsers = parser.add_subparsers(dest="command")

    crawl_parser = subparsers.add_parser("crawl", help="Run only the web crawler.")
    crawl_parser.add_argument(
        "--url", type=str, required=True, help="The target website URL to crawl."
    )
    crawl_parser.add_argument(
        "--output",
        type=str,
        default=CRAWLER_OUTPUT_FILE,
        help=f"Output file path (default: {CRAWLER_OUTPUT_FILE})",
    )

    ai_parser = subparsers.add_parser("ai", help="Run only the AI agent.")
    ai_parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Directory or file to process with the AI agent.",
    )
    ai_parser.add_argument(
        "--output",
        type=str,
        default=AI_OUTPUT_FILE,
        help=f"Output file path (default: {AI_OUTPUT_FILE})",
    )

    both_parser = subparsers.add_parser(
        "both", help="Run crawler first, then AI agent (default behavior)."
    )
    both_parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help=f"Website URL to crawl (default: {DEFAULT_URL})",
    )
    both_parser.add_argument(
        "--output",
        type=str,
        default=CRAWLER_OUTPUT_FILE,
        help=f"File to save crawler output (default: {CRAWLER_OUTPUT_FILE})",
    )

    args = parser.parse_args()

    if args.command is None:
        args.command = "both"
        args.url = DEFAULT_URL
        args.output = CRAWLER_OUTPUT_FILE

    if args.command == "crawl":
        await run_crawler(args.url, args.output)

    elif args.command == "ai":
        run_ai_agent(args.path)

    elif args.command == "both":
        output_path = await run_crawler(args.url, args.output)
        run_ai_agent(str(output_path))

if __name__ == "__main__":
    asyncio.run(main())
