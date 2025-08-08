import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://addyo.substack.com/p/the-70-problem-hard-truths-about",
        )

        with open("output.md", "w", encoding="utf-8") as f:
            f.write(result.markdown) # type: ignore
        print("Markdown content has been saved to output.md")

if __name__ == "__main__":
    asyncio.run(main())