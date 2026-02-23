"""Tests for Fred Miranda forum scraper — connection, parsing, and filter integration."""

import httpx
import respx

from monitor.filtering import is_black_chrome
from monitor.scrapers.fredmiranda import FredMirandaScraper

# Production-realistic HTML: Fred Miranda uses <table> rows with:
# - Thread titles in <h2><a class="topictitle"> inside nested <td><span><h2>
# - Pagination links (<a class="linksuperwhite pagelink">) alongside each thread
# - Admin/header links (<a class="linkbranco">)
# - "#lastmessage" fragment links for jumping to end of thread
# - Trailing slashes on thread URLs
FORUM_HTML = """\
<html><body>
<table>
  <tr>
    <td><a class="linkbranco" href="/forum/topic/9999">Rules &amp; Guidelines</a> |
        <a class="linkbranco" href="/forum/topic/8888" target="_blank">Uninsured Payment Alert!</a></td>
  </tr>
</table>
<table>
  <tr valign="top">
    <td align="center" bgcolor="#484848" nowrap="" valign="middle">
      <img height="11" src="/forum/images/threadnewnoff.gif" width="11"/>
    </td>
    <td align="left" bgcolor="#464646" nowrap="" style="border:2px solid #494949;padding:3px;"
        title="FS: Leica MP Black Chrome - Mint" valign="middle">
      <span title="FS: Leica MP Black Chrome - Mint">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/1111/">FS: Leica MP Black Chrome - Mint</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/1111/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="center" bgcolor="#484848" nowrap="" valign="middle">
      <img height="11" src="/forum/images/threadnewnoff.gif" width="11"/>
    </td>
    <td align="left" bgcolor="#464646" nowrap="" style="border:2px solid #494949;padding:3px;"
        title="FS: Canon EOS R5 Mark II Body" valign="middle">
      <span title="FS: Canon EOS R5 Mark II Body">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/2222/">FS: Canon EOS R5 Mark II Body</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/2222/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="center" bgcolor="#484848" nowrap="" valign="middle">
      <img height="11" src="/forum/images/threadnewnoff.gif" width="11"/>
    </td>
    <td align="left" bgcolor="#464646" nowrap="" style="border:2px solid #494949;padding:3px;"
        title="WTB: Leica MP 0.72" valign="middle">
      <span title="WTB: Leica MP 0.72">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/3333/">WTB: Leica MP 0.72</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/3333/1/">2</a>
          <a class="linksuperwhite pagelink" href="/forum/topic/3333/2/">3</a>
          <a class="linksuperwhite pagelink" href="/forum/topic/3333/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="center" bgcolor="#484848" nowrap="" valign="middle">
      <img height="11" src="/forum/images/threadnewnoff.gif" width="11"/>
    </td>
    <td align="left" bgcolor="#464646" nowrap="" style="border:2px solid #494949;padding:3px;"
        title="FS: Sony A7IV + lenses" valign="middle">
      <span title="FS: Sony A7IV + lenses">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/4444/">FS: Sony A7IV + lenses</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/4444/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
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
    assert listings[0].url == "https://www.fredmiranda.com/forum/topic/1111/"
    assert listings[0].price is None
    assert listings[0].source == "Fred Miranda"

    assert listings[1].title == "WTB: Leica MP 0.72"


@respx.mock
def test_scrape_ignores_pagination_and_admin_links(fredmiranda_config):
    """Pagination, #lastmessage, and admin links are not returned as listings."""
    respx.get("https://www.fredmiranda.com/forum/board/10/").mock(
        return_value=httpx.Response(200, text=FORUM_HTML)
    )

    scraper = FredMirandaScraper(fredmiranda_config)
    listings = scraper.scrape()
    scraper.close()

    urls = [listing.url for listing in listings]
    # No pagination page links
    assert not any("/1/" in u or "/2/" in u for u in urls)
    # No #lastmessage fragment links
    assert not any("#lastmessage" in u for u in urls)
    # No admin/header links
    assert not any("9999" in u or "8888" in u for u in urls)


# Production-realistic duplicate HTML: same thread appears with multiple URL
# variants (topic link, pagination page links, #lastmessage fragment)
FORUM_HTML_DUPLICATES = """\
<html><body>
<table>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="FS: Leica MP Black Chrome - Mint" valign="middle">
      <span title="FS: Leica MP Black Chrome - Mint">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/1111/">FS: Leica MP Black Chrome - Mint</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/1111/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="FS: Leica MP Black Chrome - Mint" valign="middle">
      <span title="FS: Leica MP Black Chrome - Mint">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/1111/">FS: Leica MP Black Chrome - Mint</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/1111/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="WTB: Leica MP 0.58" valign="middle">
      <span title="WTB: Leica MP 0.58">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/2222/">WTB: Leica MP 0.58</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/2222/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
</table>
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
<table>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="FS: Leica MP Black Chrome 0.72 - LNIB" valign="middle">
      <span title="FS: Leica MP Black Chrome 0.72 - LNIB">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/5001/">FS: Leica MP Black Chrome 0.72 - LNIB</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/5001/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="FS: Leica MP Black Paint - Rare" valign="middle">
      <span title="FS: Leica MP Black Paint - Rare">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/5002/">FS: Leica MP Black Paint - Rare</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/5002/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="FS: Leica MP 0.58" valign="middle">
      <span title="FS: Leica MP 0.58">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/5003/">FS: Leica MP 0.58</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/5003/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
  <tr valign="top">
    <td align="left" bgcolor="#464646" style="border:2px solid #494949;padding:3px;"
        title="FS: Nikon F3 HP" valign="middle">
      <span title="FS: Nikon F3 HP">
        <h2 style="display: inline; line-height: 14px;">
          <a class="topictitle" href="/forum/topic/5004/">FS: Nikon F3 HP</a>
        </h2>
        <span style="font-size:8px">
          <a class="linksuperwhite pagelink" href="/forum/topic/5004/#lastmessage">end</a>
        </span>
      </span>
    </td>
  </tr>
</table>
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
