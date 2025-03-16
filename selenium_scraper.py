from selenium.webdriver import ChromeOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time  # Added for delays

def scrape_website(url):
    """
    Scrapes the given URL using Selenium and returns the page source.
    """
    print(f"Scraping URL: {url}...")
    
    # Configure headless Chrome options
    options = ChromeOptions()
    options.add_argument("--headless")  # Run headless Chrome
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Automatically download and manage ChromeDriver
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)  # Navigate to the provided URL
        
        # Add delays for dynamic content loading
        print("Waiting for initial page load...")
        time.sleep(20)  # Initial wait for basic content
        
        # Additional wait for dynamic elements (adjust based on content)
        print("Waiting for dynamic content to load...")
        time.sleep(15)  # Adjust this value based on content complexity
        
        html = driver.page_source  # Get the HTML content of the page
    finally:
        driver.quit()  # Ensure the browser closes even if an error occurs

    return html



def extract_body_content(html_content):
    """
    Extracts the body content from the HTML.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    """
    Cleans the body content by removing scripts, styles, and unnecessary whitespace.
    """
    soup = BeautifulSoup(body_content, "html.parser")

    # Remove script and style tags
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


# Main Execution
if __name__ == "__main__":
    url_to_scrape = "https://www.postgraduate.study.cam.ac.uk/courses"
    
    # Generate safe filename from URL
    filename = url_to_scrape.replace("https://", "").replace("/", "_") + ".txt"
    
    try:
        # Scrape and clean content
        html = scrape_website(url_to_scrape)
        cleaned_content = clean_body_content(html)
        
        # Save to file
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
            
        print(f"Content saved to: {filename}")
        
    except Exception as e:
        print(f"Error: {str(e)}")