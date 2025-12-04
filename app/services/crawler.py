import re
import urllib.parse
from bs4 import BeautifulSoup
from .scraper import scrape_page

def is_internal_link(base_url: str, target_url: str) -> bool:
    base_domain = urllib.parse.urlparse(base_url).netloc
    target_domain = urllib.parse.urlparse(target_url).netloc
    return base_domain == target_domain

def normalize_url(base_url: str, link: str) -> str:
    return urllib.parse.urljoin(base_url, link)

def extract_links(base_url: str, html: str) -> set:
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all("a", href=True):
        url = normalize_url(base_url, tag["href"])
        if is_internal_link(base_url, url):
            links.add(url)

    return links

def crawl_website(start_url: str, max_pages: int = 10):
    """
    Crawls website up to max_pages and returns a dict:
        {url: scraped_text}
    """

    to_visit = {start_url}
    visited = set()
    results = {}

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue

        print(f"🔎 Crawling: {url}")
        html = scrape_page(url)
        if not html:
            visited.add(url)
            continue

        results[url] = html
        visited.add(url)

        # get new internal links
        links = extract_links(start_url, html)
        to_visit.update(links - visited)

    return results
