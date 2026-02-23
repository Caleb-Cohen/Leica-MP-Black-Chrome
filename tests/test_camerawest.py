"""Tests for Camera West scraper — connection, parsing, and filter integration."""

import httpx
import respx

from monitor.filtering import is_black_chrome
from monitor.scrapers.camerawest import CameraWestScraper

# Production-realistic Shopify suggest API response.  Real responses include
# many additional fields beyond what the scraper needs (available, body, id,
# image, tags, type, variants, vendor, featured_image, etc.).  The mock must
# carry these so tests prove the scraper correctly extracts the fields it
# cares about while ignoring the rest.
SHOPIFY_RESPONSE = {
    "resources": {
        "results": {
            "products": [
                {
                    "available": True,
                    "body": "<p>The Leica MP 0.72 is a mechanical rangefinder camera.</p>",
                    "compare_at_price_max": "5295.00",
                    "compare_at_price_min": "5295.00",
                    "handle": "leica-mp-072-black-chrome",
                    "id": 14700000000001,
                    "image": "https://cdn.shopify.com/s/files/1/example/leica-mp.jpg",
                    "price": "5295.00",
                    "price_max": "5295.00",
                    "price_min": "5295.00",
                    "tags": ["in-stock", "Leica M", "New", "Published"],
                    "title": "Leica MP 0.72 Black Chrome",
                    "type": "Film Cameras (New)",
                    "url": "/products/leica-mp-072-black-chrome?_pos=1&_psq=leica+mp&_ss=e&_v=1.0",
                    "variants": [],
                    "vendor": "Leica",
                    "featured_image": {
                        "alt": "Leica MP 0.72 Black Chrome",
                        "aspect_ratio": 1.0,
                        "height": 1500,
                        "url": "https://cdn.shopify.com/s/files/1/example/leica-mp.jpg",
                        "width": 1500,
                    },
                },
                {
                    "available": True,
                    "body": "<p>The Leica M-A is a purely mechanical rangefinder.</p>",
                    "compare_at_price_max": "5195.00",
                    "compare_at_price_min": "5195.00",
                    "handle": "leica-m-a-silver",
                    "id": 14700000000002,
                    "image": "https://cdn.shopify.com/s/files/1/example/leica-ma.jpg",
                    "price": "5195.00",
                    "price_max": "5195.00",
                    "price_min": "5195.00",
                    "tags": ["in-stock", "Leica M", "New", "Published"],
                    "title": "Leica M-A (Typ 127) Silver Chrome",
                    "type": "Film Cameras (New)",
                    "url": "/products/leica-m-a-silver?_pos=2&_psq=leica+mp&_ss=e&_v=1.0",
                    "variants": [],
                    "vendor": "Leica",
                    "featured_image": {
                        "alt": "Leica M-A (Typ 127) Silver Chrome",
                        "aspect_ratio": 1.0,
                        "height": 1500,
                        "url": "https://cdn.shopify.com/s/files/1/example/leica-ma.jpg",
                        "width": 1500,
                    },
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
def test_scrape_uses_handle_not_url_field(camerawest_config):
    """Scraper constructs URL from handle, not from the Shopify url field with query params."""
    respx.get("https://camerawest.com/search/suggest.json").mock(
        return_value=httpx.Response(200, json=SHOPIFY_RESPONSE)
    )

    scraper = CameraWestScraper(camerawest_config)
    listings = scraper.scrape()
    scraper.close()

    # URL should be base + handle, NOT the raw Shopify url which has ?_pos=... params
    assert listings[0].url == "https://camerawest.com/products/leica-mp-072-black-chrome"
    assert "?_pos=" not in listings[0].url
    assert "?_psq=" not in listings[0].url


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
                    "available": True,
                    "body": "",
                    "handle": "leica-mp-072-black-chrome",
                    "id": 14700000000001,
                    "image": "https://cdn.shopify.com/s/files/1/example/mp.jpg",
                    "price": "5295.00",
                    "price_max": "5295.00",
                    "price_min": "5295.00",
                    "tags": ["in-stock"],
                    "title": "Leica MP 0.72 Black Chrome",
                    "type": "Film Cameras (New)",
                    "url": "/products/leica-mp-072-black-chrome?_pos=1&_psq=leica+mp&_ss=e&_v=1.0",
                    "variants": [],
                    "vendor": "Leica",
                },
                {
                    "available": True,
                    "body": "",
                    "handle": "leica-m-a-silver",
                    "id": 14700000000002,
                    "image": "https://cdn.shopify.com/s/files/1/example/ma.jpg",
                    "price": "5195.00",
                    "price_max": "5195.00",
                    "price_min": "5195.00",
                    "tags": ["in-stock"],
                    "title": "Leica M-A (Typ 127) Silver Chrome",
                    "type": "Film Cameras (New)",
                    "url": "/products/leica-m-a-silver?_pos=2&_psq=leica+mp&_ss=e&_v=1.0",
                    "variants": [],
                    "vendor": "Leica",
                },
                {
                    "available": True,
                    "body": "",
                    "handle": "leica-mp-black-paint",
                    "id": 14700000000003,
                    "image": "https://cdn.shopify.com/s/files/1/example/mp-bp.jpg",
                    "price": "9500.00",
                    "price_max": "9500.00",
                    "price_min": "9500.00",
                    "tags": ["in-stock"],
                    "title": "Leica MP Black Paint",
                    "type": "Film Cameras (New)",
                    "url": "/products/leica-mp-black-paint?_pos=3&_psq=leica+mp&_ss=e&_v=1.0",
                    "variants": [],
                    "vendor": "Leica",
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
