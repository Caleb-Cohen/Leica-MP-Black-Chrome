"""Tests for MapCamera scraper — connection, parsing, and filter integration."""

import httpx
import respx

from monitor.filtering import is_black_chrome
from monitor.scrapers.mapcamera import MapCameraScraper

MAPCAMERA_HTML = """\
<html><body>
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
