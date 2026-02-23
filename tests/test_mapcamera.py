"""Tests for MapCamera scraper — connection, parsing, and filter integration.

MapCamera (mapcamera.com) blocks automated requests with 503 responses, so the
exact production HTML cannot be fetched for verification.  The scraper uses a
cascade of CSS selector fallbacks:

  1. .p-item  (primary)
  2. .product-item
  3. .item-list li
  4. [class*='product']
  5. [class*='item']
  6. a[href*='/item/'], a[href*='/product/']  (link-only fallback)

Each fallback path is tested below so the scraper keeps working if MapCamera
changes its CSS classes.
"""

import httpx
import respx

from monitor.filtering import is_black_chrome
from monitor.scrapers.mapcamera import MapCameraScraper

# --- Primary selector: .p-item with .p-item__name --------------------------

MAPCAMERA_HTML = """\
<html><body>
<div class="search-results">
  <div class="p-item">
    <a href="/item/1234">
      <span class="p-item__name">Leica MP 0.72 Black Chrome</span>
    </a>
    <span class="price">\u00a5748,000</span>
  </div>
  <div class="p-item">
    <a href="/item/5678">
      <span class="p-item__name">Leica M6 Black</span>
    </a>
    <span class="price">\u00a5598,000</span>
  </div>
</div>
</body></html>
"""


@respx.mock
def test_scrape_returns_listings(mapcamera_config):
    """Mocked HTML with .p-item elements is parsed into Listing objects."""
    respx.get("https://www.mapcamera.com/search").mock(
        return_value=httpx.Response(200, text=MAPCAMERA_HTML)
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    assert len(listings) == 2
    assert listings[0].title == "Leica MP 0.72 Black Chrome"
    assert listings[0].url == "https://www.mapcamera.com/item/1234"
    assert listings[0].price == "\u00a5748,000"
    assert listings[0].source == "MapCamera"

    assert listings[1].title == "Leica M6 Black"


# --- Fallback selector: .product-item --------------------------------------

MAPCAMERA_PRODUCT_ITEM_HTML = """\
<html><body>
<div class="product-item">
  <a href="/item/2001">
    <h3 class="product-name">Leica MP 0.72 Black Chrome</h3>
  </a>
  <span class="product-price">\u00a5748,000</span>
</div>
<div class="product-item">
  <a href="/item/2002">
    <h3 class="product-name">Leica M6 Black</h3>
  </a>
  <span class="product-price">\u00a5598,000</span>
</div>
</body></html>
"""


@respx.mock
def test_scrape_product_item_fallback(mapcamera_config):
    """When .p-item is absent, .product-item selector is used."""
    respx.get("https://www.mapcamera.com/search").mock(
        return_value=httpx.Response(200, text=MAPCAMERA_PRODUCT_ITEM_HTML)
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    assert len(listings) == 2
    assert listings[0].title == "Leica MP 0.72 Black Chrome"
    assert listings[0].url == "https://www.mapcamera.com/item/2001"
    assert listings[0].price == "\u00a5748,000"


# --- Fallback selector: .item-list li ---------------------------------------

MAPCAMERA_ITEM_LIST_HTML = """\
<html><body>
<ul class="item-list">
  <li>
    <a href="/item/3001">
      <span class="item-name">Leica MP 0.72 Black Chrome</span>
    </a>
    <span class="item-price">\u00a5748,000</span>
  </li>
  <li>
    <a href="/item/3002">
      <span class="item-name">Leica M6 Black</span>
    </a>
    <span class="item-price">\u00a5598,000</span>
  </li>
</ul>
</body></html>
"""


@respx.mock
def test_scrape_item_list_fallback(mapcamera_config):
    """When .p-item and .product-item are absent, .item-list li selector is used."""
    respx.get("https://www.mapcamera.com/search").mock(
        return_value=httpx.Response(200, text=MAPCAMERA_ITEM_LIST_HTML)
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    assert len(listings) == 2
    assert listings[0].title == "Leica MP 0.72 Black Chrome"
    assert listings[0].url == "https://www.mapcamera.com/item/3001"


# --- Fallback selector: link-only fallback ----------------------------------

MAPCAMERA_LINK_FALLBACK_HTML = """\
<html><body>
<div class="results">
  <a href="/item/4001">Leica MP 0.72 Black Chrome</a>
  <a href="/item/4002">Leica M6 Black</a>
  <a href="/product/4003">Leica MP 0.58</a>
  <a href="/other/4004">Something else (no match)</a>
</div>
</body></html>
"""


@respx.mock
def test_scrape_link_fallback(mapcamera_config):
    """When no container selectors match, the link-based fallback finds item/product links."""
    respx.get("https://www.mapcamera.com/search").mock(
        return_value=httpx.Response(200, text=MAPCAMERA_LINK_FALLBACK_HTML)
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    # Links with /item/ or /product/ in href AND "leica" in text are returned
    # The /other/ link is excluded (no /item/ or /product/ in href)
    assert len(listings) == 3
    assert listings[0].title == "Leica MP 0.72 Black Chrome"
    assert listings[0].url == "https://www.mapcamera.com/item/4001"
    assert listings[0].price is None  # link fallback has no price element

    assert listings[1].title == "Leica M6 Black"
    assert listings[2].title == "Leica MP 0.58"
    assert listings[2].url == "https://www.mapcamera.com/product/4003"


@respx.mock
def test_scrape_connection_failure(mapcamera_config):
    """Connection error returns an empty list instead of crashing."""
    respx.get("https://www.mapcamera.com/search").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    assert listings == []


@respx.mock
def test_scrape_empty_html(mapcamera_config):
    """Empty/no-results HTML returns an empty list."""
    respx.get("https://www.mapcamera.com/search").mock(
        return_value=httpx.Response(200, text="<html><body><p>No results</p></body></html>")
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    assert listings == []


# --- Filter integration with primary selector ------------------------------

MAPCAMERA_MIXED_HTML = """\
<html><body>
<div class="p-item">
  <a href="/item/1001">
    <span class="p-item__name">Leica MP 0.72 Black Chrome</span>
  </a>
  <span class="price">\u00a5748,000</span>
</div>
<div class="p-item">
  <a href="/item/1002">
    <span class="p-item__name">Leica MP Black Paint</span>
  </a>
  <span class="price">\u00a51,200,000</span>
</div>
<div class="p-item">
  <a href="/item/1003">
    <span class="p-item__name">Leica M6 Classic</span>
  </a>
  <span class="price">\u00a5398,000</span>
</div>
</body></html>
"""


@respx.mock
def test_scrape_with_filter_returns_matches(mapcamera_config):
    """Scraper results filtered through is_black_chrome return only matching listings."""
    respx.get("https://www.mapcamera.com/search").mock(
        return_value=httpx.Response(200, text=MAPCAMERA_MIXED_HTML)
    )

    scraper = MapCameraScraper(mapcamera_config)
    listings = scraper.scrape()
    scraper.close()

    matches = [listing for listing in listings if is_black_chrome(listing)]
    assert len(matches) == 1
    assert matches[0].title == "Leica MP 0.72 Black Chrome"
