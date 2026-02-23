"""Camera West scraper (Shopify-based store)."""

from __future__ import annotations

import logging

from monitor.scrapers.base import BaseScraper, Listing

logger = logging.getLogger(__name__)

SEARCH_URL = "https://camerawest.com/search/suggest.json"
SEARCH_PARAMS = {"q": "leica mp", "resources[type]": "product"}
PRODUCT_BASE = "https://camerawest.com/products/"


class CameraWestScraper(BaseScraper):
    """Scrape Camera West for Leica MP listings via Shopify suggest API."""

    name = "Camera West"

    def scrape(self) -> list[Listing]:
        logger.info("Scraping Camera West...")
        try:
            resp = self.client.get(SEARCH_URL, params=SEARCH_PARAMS)
            resp.raise_for_status()
        except Exception:
            logger.exception("Failed to fetch Camera West")
            return []

        try:
            data = resp.json()
            products = data.get("resources", {}).get("results", {}).get("products", [])
        except Exception:
            logger.exception("Failed to parse Camera West JSON")
            return []

        listings = []
        for product in products:
            title = product.get("title", "")
            handle = product.get("handle", "")
            price = product.get("price", "")
            url = f"{PRODUCT_BASE}{handle}" if handle else product.get("url", "")

            if price:
                price = f"${price}" if not str(price).startswith("$") else price

            listings.append(Listing(title=title, url=url, price=price, source=self.name))

        logger.info("Camera West: found %d raw listings", len(listings))
        return listings
