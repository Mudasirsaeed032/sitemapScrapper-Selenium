import scrapy
from scrapy.utils.project import get_project_settings

class OxfordSpider(scrapy.Spider):
    name = "oxford"
    custom_settings = {
    'ROBOTSTXT_OBEY': True,
    'DOWNLOAD_DELAY': 2,
    'AUTOTHROTTLE_ENABLED': True,
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'REDIRECT_ENABLED': True,
    'HTTPERROR_ALLOWED_CODES': [301, 302, 403]  # Allow 403 to log instead of failing
    }

    def start_requests(self):
        # Use your filtered URLs here
        try:
            with open("filtered_urls.txt", "r") as f:
                filtered_urls = [line.strip() for line in f.readlines()]
        except FileNotFoundError:
            self.log("filtered_urls.txt not found. Make sure to run the export script first.")
            return
        for url in filtered_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extract all text from the page (unstructured)
        page_text = response.xpath('//body//text()').getall()
        cleaned_text = '\n'.join([text.strip() for text in page_text if text.strip()])
        
        # Save to a file named after the URL
        filename = response.url.replace("https://", "").replace("/", "_") + ".txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        self.log(f"Saved: {filename}")