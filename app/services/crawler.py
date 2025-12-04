import asyncio
import logging
from typing import Dict, Set
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)


def _is_same_domain(base_url: str, target_url: str) -> bool:
    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc
    return target_domain == "" or target_domain == base_domain


async def _crawl_website_async(start_url: str, max_pages: int = 10) -> Dict[str, str]:
    logger.info(f"[Playwright] Starting crawl at {start_url} (max_pages={max_pages})")

    to_visit: Set[str] = {start_url}
    visited: Set[str] = set()
    results: Dict[str, str] = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_extra_http_headers({
            "User-Agent": "website-to-chatbot/1.0 (Playwright crawler)"
        })

        base_domain = urlparse(start_url).netloc

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop()
            if url in visited:
                continue

            logger.info(f"[Playwright] Crawling URL: {url}")

            try:
                # 👉 Correct way: response comes from goto()
                response = await page.goto(url, wait_until="networkidle", timeout=30000)
                status = response.status if response else None

                if not response or status >= 400:
                    logger.warning(f"[Playwright] Skipping {url}, bad status={status}")
                    visited.add(url)
                    continue

                # Extract visible text (DOM-based)
                text = await page.evaluate("() => document.body.innerText || ''")
                text = " ".join(text.split())

                if len(text) < 50:
                    logger.warning(f"[Playwright] Insufficient text at {url}")
                    visited.add(url)
                    continue

                # Save
                results[url] = text
                visited.add(url)

                # Extract all links from the DOM
                hrefs = await page.eval_on_selector_all(
                    "a[href]",
                    "els => els.map(e => e.href)"   # absolute URLs via DOM
                )

                for link in hrefs:
                    if _is_same_domain(start_url, link):
                        if link not in visited and link not in to_visit:
                            to_visit.add(link)

            except Exception as e:
                logger.exception(f"[Playwright] Error while crawling {url}: {e}")
                visited.add(url)
                continue

        await browser.close()

    logger.info(f"[Playwright] Finished crawling. Total pages collected: {len(results)}")
    return results


def crawl_website(start_url: str, max_pages: int = 10) -> Dict[str, str]:
    return asyncio.run(_crawl_website_async(start_url, max_pages))
