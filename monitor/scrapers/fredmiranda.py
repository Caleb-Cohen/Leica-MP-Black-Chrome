"""Fred Miranda Buy & Sell forum scraper."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from monitor.scrapers.base import BaseScraper, Listing

logger = logging.getLogger(__name__)

FORUM_URL = "https://fredmiranda.com/forum/board/10/"
BASE_URL = "https://fredmiranda.com"


class FredMirandaScraper(BaseScraper):
    """Scrape Fred Miranda Buy & Sell forum thread titles."""

    name = "Fred Miranda"

    def scrape(self) -> list[Listing]:
        logger.info("Scraping Fred Miranda...")
        try:
            resp = self.client.get(FORUM_URL)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch Fred Miranda")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        listings = []

        # Fred Miranda forum threads are in table rows or list items
        # Thread links typically point to /forum/topic/...
        thread_links = soup.select("a[href*='/forum/topic/']")

        seen_urls = set()
        for link in thread_links:
            title = link.get_text(strip=True)
            href = link.get("href", "")

            if not title:
                continue

            url = href if href.startswith("http") else f"{BASE_URL}{href}"

            # Deduplicate within this scrape (same thread can appear multiple times)
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Only include threads that mention both "leica" and "mp" in the title
            title_lower = title.lower()
            if "leica" not in title_lower or "mp" not in title_lower:
                continue

            listings.append(Listing(title=title, url=url, price=None, source=self.name))

        logger.info("Fred Miranda: found %d raw listings", len(listings))
        return listings
