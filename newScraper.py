import requests
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from collections import deque

sitemap_url = "https://www.ox.ac.uk/sitemap.xml?page=1"
max_depth = 2
keywords = ['masters', 'postgraduate', 'msc', 'ma', 'mphil', 'graduate']
data = []
visited = set()
queue = deque()

try:
    # First stage: Get initial URLs from sitemap
    response = requests.get(sitemap_url)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls = [elem.text for elem in root.findall('.//ns:loc', namespaces)]
    
    # Filter initial URLs and add to queue with depth 0
    filtered_urls = [url for url in urls if "/admissions/graduate" in url]
    for url in filtered_urls:
        queue.append((url, 0))

    # Second stage: Crawl and scrape
    while queue:
        current_url, depth = queue.popleft()
        
        if current_url in visited:
            continue
        visited.add(current_url)
        
        try:
            print(f"Processing {current_url} (depth {depth})")
            res = requests.get(current_url, timeout=10)
            res.raise_for_status()
            
            # Parse and clean content
            soup = BeautifulSoup(res.text, 'html.parser')
            for tag in soup(['script', 'style']):
                tag.decompose()
                
            text = soup.get_text(separator='\n', strip=True)
            cleaned_text = re.sub(r'\n+', '\n', text).strip()
            
            # Save data
            data.append({
                'url': current_url,
                'title': soup.title.string.strip() if soup.title else 'N/A',
                'content': cleaned_text,
                'depth': depth,
                'source_url': current_url
            })
            
            # Extract links for next level if within depth limit
            if depth < max_depth:
                for a in soup.find_all('a', href=True):
                    link = urljoin(current_url, a['href'])
                    if (link not in visited and 
                        any(kw in link.lower() for kw in keywords) and 
                        'ox.ac.uk' in link.lower()):
                        
                        queue.append((link, depth + 1))
                        print(f"  Found: {link} (depth {depth + 1})")

        except Exception as e:
            print(f"Error processing {current_url}: {str(e)[:100]}")

    # Save results
    with open('university_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nScraped {len(data)} pages across {max_depth + 1} levels")

except requests.RequestException as e:
    print(f"Sitemap error: {e}")
except ET.ParseError as e:
    print(f"XML parsing error: {e}")