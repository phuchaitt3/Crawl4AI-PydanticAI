import os
import sys
import psutil
import asyncio
import requests
from xml.etree import ElementTree

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def crawl_parallel(urls: List[str], max_concurrent: int = 3):
    print("\n=== Parallel Crawling with Browser Reuse + Memory Check ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,   # corrected from 'verbos=False'
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1
                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

import requests
from xml.etree import ElementTree
from typing import List

# It's good practice to rename the function to reflect its more general purpose
def get_urls_from_sitemaps(sitemap_urls: List[str]) -> List[str]:
    """
    Fetches all URLs from a list of sitemap XML files.

    Args:
        sitemap_urls (List[str]): A list of sitemap URLs to process.

    Returns:
        List[str]: A single, combined list of all unique URLs found.
    """
    all_urls = [
        
    ]
    
    # The namespace is usually the same for all sitemaps
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Loop over each sitemap URL provided in the list
    for sitemap_url in sitemap_urls:
        print(f"Processing sitemap: {sitemap_url}")
        try:
            response = requests.get(sitemap_url)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # Parse the XML content
            root = ElementTree.fromstring(response.content)

            # Find all <loc> tags and extract their text content
            urls_from_sitemap = [loc.text for loc in root.findall('.//ns:loc', namespace)]
            
            # Add the found URLs to our main list
            all_urls.extend(urls_from_sitemap)

        except requests.exceptions.RequestException as e:
            # Handle network-related errors (e.g., invalid URL, no connection)
            print(f"Error fetching sitemap {sitemap_url}: {e}")
        except ElementTree.ParseError as e:
            # Handle cases where the content is not valid XML
            print(f"Error parsing XML for {sitemap_url}: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred for {sitemap_url}: {e}")

    # Optional: Return only unique URLs in case of duplicates across sitemaps
    # The list(dict.fromkeys(...)) pattern is a fast way to get unique items while preserving order.
    return list(dict.fromkeys(all_urls))

# def get_pydantic_ai_docs_urls():
#     """
#     Fetches all URLs from the Pydantic AI documentation.
#     Uses the sitemap (https://ai.pydantic.dev/sitemap.xml) to get these URLs.
    
#     Returns:
#         List[str]: List of URLs
#     """            
#     sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
#     try:
#         response = requests.get(sitemap_url)
#         response.raise_for_status()
        
#         # Parse the XML
#         root = ElementTree.fromstring(response.content)
        
#         # Extract all URLs from the sitemap
#         # The namespace is usually defined in the root element
#         namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
#         urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
#         return urls
#     except Exception as e:
#         print(f"Error fetching sitemap: {e}")
#         return []        

async def main():
    urls = get_pydantic_ai_docs_urls()
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        await crawl_parallel(urls, max_concurrent=10)
    else:
        print("No URLs found to crawl")    

if __name__ == "__main__":
    asyncio.run(main())
