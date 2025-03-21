import os
import sys
import psutil
import asyncio
import json
from datetime import datetime
from typing import List
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

__location__ = os.path.dirname(os.path.abspath(__file__))
__output__ = os.path.join(__location__, "output")
os.makedirs(__output__, exist_ok=True)

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

async def crawl_parallel(urls: List[str], batch_id: str, max_concurrent: int = 3):
    print(f"\n=== Batch {batch_id} Crawling ===")
    peak_memory = 0
    process = psutil.Process(os.getpid())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Memory: {current_mem // (1024 * 1024)} MB")

    async def save_result(result, url: str):
        """Save crawled content to markdown and json files"""
        try:
            base_name = url.replace("https://", "").replace("/", "_")[:150]
            
            # Generate filenames
            md_filename = f"{base_name}_{batch_id}_{timestamp}.md"
            json_filename = f"{base_name}_{batch_id}_{timestamp}.json"
            md_path = os.path.join(__output__, md_filename)
            json_path = os.path.join(__output__, json_filename)

            # Extract university name from URL
            parsed_url = urlparse(url)
            domain_parts = parsed_url.netloc.replace("www.", "").split(".")
            university_name = " ".join([part.capitalize() for part in domain_parts[:2]])

            # Prepare content
            md_content = f"# Scraped Content from {url}\n\n"
            md_content += f"**Crawled At:** {datetime.now().isoformat()}\n\n"
            md_content += result.markdown

            # Write markdown
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            # Write JSON
            json_data = {
                "University Name": university_name,
                "Link": url,
                "Content": result.markdown
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)

            print(f"Saved: {md_filename} and {json_filename}")
            
        except Exception as e:
            print(f"Failed to save {url}: {str(e)}")

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = [crawler.arun(url=url, config=crawl_config, session_id=f"session_{batch_id}_{i+j}") 
                    for j, url in enumerate(batch)]

            log_memory(prefix=f"Batch {batch_id} - Pre {i//max_concurrent + 1}: ")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            log_memory(prefix=f"Batch {batch_id} - Post {i//max_concurrent + 1}: ")

            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    await save_result(result, url)
                    success_count += 1
                else:
                    fail_count += 1

        print(f"\nBatch {batch_id} Summary:")
        print(f"  Success: {success_count}")
        print(f"  Failures: {fail_count}")

    finally:
        await crawler.close()
        log_memory(prefix="Final: ")

def get_urls_from_filtered_file():
    """Read URLs from filtered_urls.txt"""
    try:
        file_path = os.path.join(__location__, "filtered_urls.txt")
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading URLs: {e}")
        return []

async def main():
    urls = get_urls_from_filtered_file()
    if urls:
        print(f"Found {len(urls)} URLs")
        await crawl_parallel(urls, "initial", 10)
        
        # Scheduled crawl
        print("\n=== Scheduling next crawl ===")
        await asyncio.sleep(120)
        await crawl_parallel(urls, "scheduled", 10)
    else:
        print("No URLs found")

if __name__ == "__main__":
    asyncio.run(main())