import os
import feedparser
import requests
from bs4 import BeautifulSoup

rss_url = "http://feeds.bbci.co.uk/news/world/rss.xml"
feed = feedparser.parse(rss_url)

def extract_article_content(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        print(f"Failed to fetch {url}")
        return None

    soup = BeautifulSoup(res.content, "html.parser")
    paragraphs = soup.find_all("div", {"data-component": "text-block"})
    if not paragraphs:
        print(f"No paragraphs found in {url}")
        return None

    return "\n".join(p.get_text(strip=True) for p in paragraphs)

output_dir = "bbc_articles_txt"
os.makedirs(output_dir, exist_ok=True)

print(f"Found {len(feed.entries)} articles")

for i, entry in enumerate(feed.entries[:50], start=1):
    print(f"Fetching {entry.link} ...")
    content = extract_article_content(entry.link)
    if content:
        filename = re.sub(r'[\\/*?:"<>|]',"", entry.title)
        filepath = os.path.join(output_dir, f"{i:03d}_{filename}.txt")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(entry.title + "\n\n")
            f.write(content)
        
        print(f"Saved: {filepath}")
    else:
        print(f"Failed to extract: {entry.link}")
