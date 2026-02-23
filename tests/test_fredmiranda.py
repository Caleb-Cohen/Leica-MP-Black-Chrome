"""Tests for Fred Miranda forum scraper — connection, parsing, and filter integration."""

import httpx
import respx

from monitor.filtering import is_black_chrome
from monitor.scrapers.fredmiranda import FredMirandaScraper

FORUM_HTML = """\
<html><body>
<table>
  <tr><td><a href="/forum/topic/1111">FS: Leica MP Black Chrome - Mint</a></td></tr>
  <tr><td><a href="/forum/topic/2222">FS: Canon EOS R5 Mark II Body</a></td></tr>
  <tr><td><a href="/forum/topic/3333">WTB: Leica MP 0.72</a></td></tr>
  <tr><td><a href="/forum/topic/4444">FS: Sony A7IV + lenses</a></td></tr>
</table>
</body></html>
"""


@respx.mock
def test_scrape_returns_listings(fredmiranda_config):
    """Mocked forum HTML is parsed; only threads with 'leica mp' are returned."""
    respx.get("https://www.fredmiranda.com/forum/board/10/").mock(
        return_value=httpx.Response(200, text=FORUM_HTML)
    )

    scraper = FredMirandaScraper(fredmiranda_config)
    listings = scraper.scrape()
    scraper.close()

    assert len(listings) == 2
    assert listings[0].title == "FS: Leica MP Black Chrome - Mint"
    assert listings[0].url == "https://www.fredmiranda.com/forum/topic/1111"
    assert listings[0].price is None
    assert listings[0].source == "Fred Miranda"

    assert listings[1].title == "WTB: Leica MP 0.72"


FORUM_HTML_DUPLICATES = """\
<html><body>
<a href="/forum/topic/1111">FS: Leica MP Black Chrome - Mint</a>
<a href="/forum/topic/1111">FS: Leica MP Black Chrome - Mint</a>
<a href="/forum/topic/2222">WTB: Leica MP 0.58</a>
</body></html>
"""


@respx.mock
def test_scrape_deduplicates(fredmiranda_config):
    """Duplicate thread links within a page are deduplicated."""
    respx.get("https://www.fredmiranda.com/forum/board/10/").mock(
        return_value=httpx.Response(200, text=FORUM_HTML_DUPLICATES)
    )

    scraper = FredMirandaScraper(fredmiranda_config)
    listings = scraper.scrape()
    scraper.close()

    assert len(listings) == 2
    urls = [listing.url for listing in listings]
    assert len(set(urls)) == 2


@respx.mock
def test_scrape_connection_failure(fredmiranda_config):
    """Connection error returns an empty list instead of crashing."""
    respx.get("https://www.fredmiranda.com/forum/board/10/").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )

    scraper = FredMirandaScraper(fredmiranda_config)
    listings = scraper.scrape()
    scraper.close()

    assert listings == []


FORUM_HTML_MIXED = """\
<html><body>
<a href="/forum/topic/5001">FS: Leica MP Black Chrome 0.72 - LNIB</a>
<a href="/forum/topic/5002">FS: Leica MP Black Paint - Rare</a>
<a href="/forum/topic/5003">FS: Leica MP 0.58</a>
<a href="/forum/topic/5004">FS: Nikon F3 HP</a>
</body></html>
"""


@respx.mock
def test_scrape_with_filter_returns_matches(fredmiranda_config):
    """Scraper results filtered through is_black_chrome return only matching listings."""
    respx.get("https://www.fredmiranda.com/forum/board/10/").mock(
        return_value=httpx.Response(200, text=FORUM_HTML_MIXED)
    )

    scraper = FredMirandaScraper(fredmiranda_config)
    listings = scraper.scrape()
    scraper.close()

    # Scraper itself only filters for "leica mp" — it returns all 3 leica mp threads
    assert len(listings) == 3

    # The is_black_chrome filter further narrows to black chrome variants
    matches = [listing for listing in listings if is_black_chrome(listing)]
    assert len(matches) == 2
    titles = [m.title for m in matches]
    assert "FS: Leica MP Black Chrome 0.72 - LNIB" in titles
    assert "FS: Leica MP 0.58" in titles  # bare "Leica MP" accepted as likely black chrome
