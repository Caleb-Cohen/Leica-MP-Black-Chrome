"""Tests for Camera West scraper — connection, parsing, and filter integration."""

import httpx
import respx

from monitor.filtering import is_black_chrome
from monitor.scrapers.camerawest import CameraWestScraper

SHOPIFY_RESPONSE = {
    "resources": {
        "results": {
            "products": [
                {
                    "title": "Leica MP 0.72 Black Chrome",
                    "handle": "leica-mp-072-black-chrome",
                    "price": "5295.00",
                    "url": "/products/leica-mp-072-black-chrome",
                },
                {
                    "title": "Leica M-A (Typ 127) Silver Chrome",
                    "handle": "leica-m-a-silver",
                    "price": "5195.00",
                    "url": "/products/leica-m-a-silver",
                },
            ]
        }
    }
}


@respx.mock
def test_scrape_returns_listings(camerawest_config):
    """Mocked Shopify JSON response is parsed into Listing objects."""
    respx.get("https://camerawest.com/search/suggest.json").mock(
        return_value=httpx.Response(200, json=SHOPIFY_RESPONSE)
    )

    scraper = CameraWestScraper(camerawest_config)
    listings = scraper.scrape()
    scraper.close()

    assert len(listings) == 2
    assert listings[0].title == "Leica MP 0.72 Black Chrome"
    assert listings[0].url == "https://camerawest.com/products/leica-mp-072-black-chrome"
    assert listings[0].price == "$5295.00"
    assert listings[0].source == "Camera West"

    assert listings[1].title == "Leica M-A (Typ 127) Silver Chrome"


@respx.mock
def test_scrape_connection_failure(camerawest_config):
    """Connection error returns an empty list instead of crashing."""
    respx.get("https://camerawest.com/search/suggest.json").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    scraper = CameraWestScraper(camerawest_config)
    listings = scraper.scrape()
    scraper.close()

    assert listings == []


MIXED_SHOPIFY_RESPONSE = {
    "resources": {
        "results": {
            "products": [
                {
                    "title": "Leica MP 0.72 Black Chrome",
                    "handle": "leica-mp-072-black-chrome",
                    "price": "5295.00",
                },
                {
                    "title": "Leica M-A (Typ 127) Silver Chrome",
                    "handle": "leica-m-a-silver",
                    "price": "5195.00",
                },
                {
                    "title": "Leica MP Black Paint",
                    "handle": "leica-mp-black-paint",
                    "price": "9500.00",
                },
            ]
        }
    }
}


@respx.mock
def test_scrape_with_filter_returns_matches(camerawest_config):
    """Scraper results filtered through is_black_chrome return only matching listings."""
    respx.get("https://camerawest.com/search/suggest.json").mock(
        return_value=httpx.Response(200, json=MIXED_SHOPIFY_RESPONSE)
    )

    scraper = CameraWestScraper(camerawest_config)
    listings = scraper.scrape()
    scraper.close()

    matches = [listing for listing in listings if is_black_chrome(listing)]
    assert len(matches) == 1
    assert matches[0].title == "Leica MP 0.72 Black Chrome"
