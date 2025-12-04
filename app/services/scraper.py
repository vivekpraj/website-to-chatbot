import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)


def scrape_page(url: str) -> str:
    """
    Synchronous Playwright scraper.
    Works perfectly on Windows + FastAPI.
    """

    logger.info(f"Scraping URL: {url}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, timeout=60000, wait_until="networkidle")

            auto_scroll_sync(page)

            content = page.evaluate("() => document.body.innerText")

            browser.close()

            logger.info(f"Scraping complete. Extracted {len(content)} characters.")
            return content

    except Exception:
        logger.exception(f"Scraping failed for URL: {url}")
        return ""


def auto_scroll_sync(page):
    """Sync version of auto scroll for dynamic content."""
    page.evaluate(
        """
        () => {
            return new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 400;

                const timer = setInterval(() => {
                    const scrollHeight = document.body.scrollHeight;
                    window.scrollBy(0, distance);
                    totalHeight += distance;

                    if (totalHeight >= scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 200);
            });
        }
        """
    )
