"""MapCamera scraper (Japanese camera retailer)."""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from monitor.scrapers.base import BaseScraper, Listing

logger = logging.getLogger(__name__)

SEARCH_URL = "https://www.mapcamera.com/search"
SEARCH_PARAMS = {"keyword": "leica mp", "igngkeyword": "1"}
BASE_URL = "https://www.mapcamera.com"


class MapCameraScraper(BaseScraper):
    """Scrape MapCamera search results for Leica MP listings."""

    name = "MapCamera"

    def scrape(self) -> list[Listing]:
        logger.info("Scraping MapCamera...")
        try:
            resp = self.client.get(SEARCH_URL, params=SEARCH_PARAMS)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch MapCamera")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        listings = []

        # MapCamera uses product cards/items in search results
        # Try multiple common selectors for product listings
        items = (
            soup.select(".p-item")
            or soup.select(".product-item")
            or soup.select(".item-list li")
            or soup.select("[class*='product']")
            or soup.select("[class*='item']")
        )

        if not items:
            # Fallback: look for any links containing product-like patterns
            logger.warning("MapCamera: no product items found with known selectors, trying links")
            for link in soup.select("a[href*='/item/'], a[href*='/product/']"):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if title and "leica" in title.lower():
                    url = href if href.startswith("http") else f"{BASE_URL}{href}"
                    listings.append(Listing(title=title, url=url, price=None, source=self.name))
        else:
            for item in items:
                # Extract title from link or heading
                link = item.select_one("a")
                title_el = item.select_one(
                    "[class*='name'], [class*='title'], h2, h3, .p-item__name"
                )

                title = ""
                if title_el:
                    title = title_el.get_text(strip=True)
                elif link:
                    title = link.get_text(strip=True)

                if not title:
                    continue

                # Extract URL
                href = ""
                if link:
                    href = link.get("href", "")
                url = href if href.startswith("http") else f"{BASE_URL}{href}"

                # Extract price
                price_el = item.select_one("[class*='price']")
                price = price_el.get_text(strip=True) if price_el else None

                listings.append(Listing(title=title, url=url, price=price, source=self.name))

        logger.info("MapCamera: found %d raw listings", len(listings))
        return listings
