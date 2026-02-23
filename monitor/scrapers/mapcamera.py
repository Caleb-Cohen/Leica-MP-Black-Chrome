"""MapCamera scraper (Japanese camera retailer).

NOTE: MapCamera is protected by Akamai Bot Manager and currently blocks all
automated requests.  This scraper is intentionally excluded from the main
monitor loop until a reliable fetch strategy is implemented.  The parsing
logic and tests are kept here so they stay current with the site structure.
"""

from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from monitor.scrapers.base import BaseScraper, Listing

logger = logging.getLogger(__name__)


class MapCameraScraper(BaseScraper):
    """Scrape MapCamera search results for Leica MP listings."""

    name = "MapCamera"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.search_url = config["mapcamera_search_url"]
        self.search_keyword = config["mapcamera_search_keyword"]
        self.base_url = config["mapcamera_base_url"]

    def scrape(self) -> list[Listing]:
        logger.info("Scraping MapCamera...")
        params = {"keyword": self.search_keyword, "igngkeyword": "1"}
        try:
            resp = self.client.get(self.search_url, params=params)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch MapCamera")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        listings = []

        items = (
            soup.select(".p-item")
            or soup.select(".product-item")
            or soup.select(".item-list li")
            or soup.select("[class*='product']")
            or soup.select("[class*='item']")
        )

        if not items:
            logger.warning("MapCamera: no product items found with known selectors, trying links")
            for link in soup.select("a[href*='/item/'], a[href*='/product/']"):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                if title and "leica" in title.lower():
                    url = href if href.startswith("http") else f"{self.base_url}{href}"
                    listings.append(Listing(title=title, url=url, price=None, source=self.name))
        else:
            for item in items:
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

                href = link.get("href", "") if link else ""
                url = href if href.startswith("http") else f"{self.base_url}{href}"

                price_el = item.select_one("[class*='price']")
                price = price_el.get_text(strip=True) if price_el else None

                listings.append(Listing(title=title, url=url, price=price, source=self.name))

        logger.info("MapCamera: found %d raw listings", len(listings))
        return listings
