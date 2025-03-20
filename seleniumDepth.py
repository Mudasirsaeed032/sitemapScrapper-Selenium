from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import schedule

# Maximum depth for crawling
MAX_DEPTH = 3

def scrape_website(url):
    """Scrape a single URL and return its HTML content."""
    print(f"Scraping URL: {url}...")
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        print("Waiting for initial page load...")
        time.sleep(20)
        print("Waiting for dynamic content to load...")
        time.sleep(15)
        return driver.page_source
    finally:
        driver.quit()

def extract_body_content(html_content):
    """Extract the body content from the HTML."""
    soup = BeautifulSoup(html_content, "html.parser")
    return str(soup.body) if soup.body else ""

def clean_body_content(body_content):
    """Clean the body content by removing scripts, styles, and unnecessary whitespace."""
    soup = BeautifulSoup(body_content, "html.parser")
    for element in soup(["script", "style"]):
        element.extract()
    text = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())

def extract_links(html_content, base_url):
    """Extract all valid links from the HTML content."""
    soup = BeautifulSoup(html_content, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        # Resolve relative URLs
        full_url = urljoin(base_url, href)
        # Filter links (e.g., only keep links from the same domain)
        if full_url.startswith(base_url):
            links.add(full_url)
    return list(links)

def scrape_with_depth(url, base_url, depth=1):
    """Recursively scrape URLs up to a specified depth."""
    if depth > MAX_DEPTH:
        print(f"Reached max depth ({MAX_DEPTH}). Stopping further crawling.")
        return []

    print(f"Scraping at depth {depth}: {url}")
    try:
        # Scrape the current page
        html = scrape_website(url)
        cleaned = clean_body_content(extract_body_content(html))
        
        # Save the cleaned content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{url.replace('https://', '').replace('/', '_')}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(cleaned)
        print(f"Saved: {filename}")

        # Extract links for deeper crawling
        links = extract_links(html, base_url)
        print(f"Found {len(links)} links at depth {depth}")

        # Recursively scrape links at the next depth level
        for link in links:
            scrape_with_depth(link, base_url, depth + 1)

    except Exception as e:
        print(f"Failed to scrape {url}: {str(e)}")

def process_batch(batch_id):
    """Handle batch processing with unique filenames."""
    with open("filtered_urls.txt", "r") as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]
    
    for url in urls:
        try:
            print(f"\n=== Starting depth-based scrape for {url} ===")
            scrape_with_depth(url, base_url=url, depth=1)
        except Exception as e:
            print(f"Failed batch processing for {url}: {str(e)}")

def run_scheduler():
    """Configurable scheduler controller."""
    # For testing: 2 minutes interval, runs once
    # For production: Change to every(2).days
    schedule.every(2).minutes.do(lambda: process_batch("rescheduled"))
    
    while True:
        n_jobs = len(schedule.get_jobs())
        if n_jobs == 0:
            break
        print(f"\nNext run: {schedule.next_run()}", flush=True)
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Initial run
    print("=== Starting initial scrape ===")
    process_batch("initial")
    
    # Start scheduler (will run once for testing)
    print("\n=== Starting scheduler ===")
    run_scheduler()
    
    print("\n=== All scheduled jobs completed ===")