import requests
from xml.etree import ElementTree as ET

sitemap_url = "https://www.ox.ac.uk/sitemap.xml?page=1"

try:
    response = requests.get(sitemap_url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    root = ET.fromstring(response.content)

    # Define the namespace used in the sitemap
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    # Extract all URLs using the namespace
    urls = [elem.text for elem in root.findall('.//ns:loc', namespaces)]
    
    # Filter specific URLs and enforce HTTPS
    filtered_urls = [
        url.replace("http://", "https://")  # Convert HTTP to HTTPS
        for url in urls 
        if "/admissions/graduate" in url
    ]

    print("Filtered URLs:")
    with open("filtered_urls.txt", "w") as f:
        for url in filtered_urls:
            f.write(url + "\n")
  
    print(f"Exported {len(filtered_urls)} URLs to filtered_urls.txt")

except requests.RequestException as e:
    print(f"An error occurred while fetching the sitemap: {e}")
except ET.ParseError as e:
    print(f"An error occurred while parsing the XML: {e}")