import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.topcv.vn/viec-lam/ai-developer/1777282.html?ta_source=JobSearchList_LinkDetail&u_sr_id=eZhYJZBtmQxDVT9RLNSB4Wkk55ixGyGkyrEeJXDb_1751177482",
        )
        # Save markdown to a file
        with open("output.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)
        print("Markdown content has been saved to output.md")

if __name__ == "__main__":
    asyncio.run(main())