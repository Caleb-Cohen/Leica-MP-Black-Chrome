"""Structural validation tests — verify mock HTML mirrors real production patterns.

These tests do NOT call the scrapers.  They parse the mock HTML/JSON directly
with the same selectors the scrapers use, ensuring the mock data exercises the
real code paths.  If a mock drifts from the expected structure (e.g. someone
simplifies it for readability), these tests will catch it.

Update these tests whenever a scraper's parsing logic changes.
"""

from bs4 import BeautifulSoup

from tests.test_fredmiranda import FORUM_HTML, FORUM_HTML_DUPLICATES, FORUM_HTML_MIXED
from tests.test_mapcamera import (
    MAPCAMERA_HTML,
    MAPCAMERA_ITEM_LIST_HTML,
    MAPCAMERA_LINK_FALLBACK_HTML,
    MAPCAMERA_MIXED_HTML,
    MAPCAMERA_PRODUCT_ITEM_HTML,
)
from tests.test_camerawest import SHOPIFY_RESPONSE, MIXED_SHOPIFY_RESPONSE


# ---------------------------------------------------------------------------
# Fred Miranda: structural expectations from production (verified 2025-02)
# Production uses: <td><span><h2><a class="topictitle" href="/forum/topic/N/">
# alongside pagination links (<a class="linksuperwhite pagelink">).
# ---------------------------------------------------------------------------


class TestFredMirandaStructure:
    """Verify Fred Miranda mock HTML matches production patterns."""

    def test_thread_links_use_topictitle_class(self):
        """Production thread titles use <a class='topictitle'>."""
        soup = BeautifulSoup(FORUM_HTML, "html.parser")
        topic_links = soup.select("a.topictitle[href*='/forum/topic/']")
        all_links = soup.select("a[href*='/forum/topic/']")

        # Topic title links should be a subset of all forum/topic links
        assert len(topic_links) >= 1
        assert len(all_links) > len(topic_links), (
            "Mock should include non-topictitle links (pagination, admin) "
            "to match production noise"
        )

    def test_pagination_links_present(self):
        """Production pages include pagination and #lastmessage links."""
        soup = BeautifulSoup(FORUM_HTML, "html.parser")
        page_links = soup.select("a.linksuperwhite[href*='/forum/topic/']")
        assert len(page_links) >= 1, "Mock should include pagination links"

        # At least one #lastmessage fragment
        fragment_links = [
            a for a in page_links if "#lastmessage" in a.get("href", "")
        ]
        assert len(fragment_links) >= 1, "Mock should include #lastmessage links"

    def test_admin_links_present(self):
        """Production pages have admin/header links (class='linkbranco')."""
        soup = BeautifulSoup(FORUM_HTML, "html.parser")
        admin_links = soup.select("a.linkbranco[href*='/forum/topic/']")
        assert len(admin_links) >= 1, "Mock should include admin header links"

    def test_thread_urls_have_trailing_slash(self):
        """Production thread URLs use trailing slashes (/forum/topic/N/)."""
        soup = BeautifulSoup(FORUM_HTML, "html.parser")
        topic_links = soup.select("a.topictitle[href*='/forum/topic/']")
        for link in topic_links:
            href = link.get("href", "")
            assert href.endswith("/"), (
                f"Thread URL '{href}' should end with '/' to match production"
            )

    def test_threads_nested_in_table_rows(self):
        """Production threads sit inside <tr> → <td> → <span> → <h2> → <a>."""
        soup = BeautifulSoup(FORUM_HTML, "html.parser")
        topic_links = soup.select("a.topictitle[href*='/forum/topic/']")
        for link in topic_links:
            assert link.parent.name == "h2", "topictitle link should be inside <h2>"
            # h2 → span → td → tr
            h2 = link.parent
            span = h2.parent
            assert span.name == "span", "<h2> should be inside <span>"
            td = span.parent
            assert td.name == "td", "<span> should be inside <td>"

    def test_duplicate_mock_has_matching_structure(self):
        """The duplicate-testing mock uses the same production structure."""
        soup = BeautifulSoup(FORUM_HTML_DUPLICATES, "html.parser")
        topic_links = soup.select("a.topictitle[href*='/forum/topic/']")
        all_links = soup.select("a[href*='/forum/topic/']")

        assert len(topic_links) >= 1
        # Should include pagination/lastmessage links alongside duplicated topics
        assert len(all_links) > len(topic_links)

    def test_mixed_mock_has_matching_structure(self):
        """The filter-testing mock uses the same production structure."""
        soup = BeautifulSoup(FORUM_HTML_MIXED, "html.parser")
        topic_links = soup.select("a.topictitle[href*='/forum/topic/']")
        all_links = soup.select("a[href*='/forum/topic/']")

        assert len(topic_links) >= 2
        assert len(all_links) > len(topic_links)


# ---------------------------------------------------------------------------
# Camera West: structural expectations from Shopify suggest API (verified 2025-02)
# Production JSON includes: available, body, compare_at_price_max/min, handle,
# id, image, price, price_max/min, tags, title, type, url (with query params),
# variants, vendor, featured_image.
# ---------------------------------------------------------------------------


class TestCameraWestStructure:
    """Verify Camera West mock JSON matches production Shopify structure."""

    PRODUCTION_FIELDS = {
        "available", "body", "handle", "id", "image", "price",
        "price_max", "price_min", "tags", "title", "type",
        "url", "variants", "vendor",
    }

    def _products(self, data):
        return data["resources"]["results"]["products"]

    def test_products_nested_correctly(self):
        """Products live at resources.results.products (Shopify suggest API)."""
        products = self._products(SHOPIFY_RESPONSE)
        assert isinstance(products, list)
        assert len(products) >= 1

    def test_products_contain_production_fields(self):
        """Each product should carry the fields present in real Shopify responses."""
        for product in self._products(SHOPIFY_RESPONSE):
            present = set(product.keys())
            missing = self.PRODUCTION_FIELDS - present
            assert not missing, (
                f"Product '{product.get('title')}' is missing production fields: {missing}"
            )

    def test_url_field_has_query_params(self):
        """Production Shopify url fields include tracking query params."""
        for product in self._products(SHOPIFY_RESPONSE):
            url = product.get("url", "")
            assert "?" in url, (
                f"Product url '{url}' should include Shopify query params "
                "(?_pos=...&_psq=...) to match production"
            )

    def test_mixed_response_has_production_fields(self):
        """The filter-testing mock also carries production fields."""
        for product in self._products(MIXED_SHOPIFY_RESPONSE):
            present = set(product.keys())
            missing = self.PRODUCTION_FIELDS - present
            assert not missing, (
                f"Mixed product '{product.get('title')}' is missing: {missing}"
            )


# ---------------------------------------------------------------------------
# MapCamera: structural expectations for the primary .p-item selector path.
# Production site blocks automated requests so exact structure cannot be
# verified externally; these tests ensure mock consistency with scraper logic.
# ---------------------------------------------------------------------------


class TestMapCameraStructure:
    """Verify MapCamera mock HTML matches the scraper's selector expectations."""

    def test_primary_mock_uses_p_item(self):
        """Primary mock should use .p-item containers."""
        soup = BeautifulSoup(MAPCAMERA_HTML, "html.parser")
        items = soup.select(".p-item")
        assert len(items) >= 1
        # Each .p-item should have a link and a name element
        for item in items:
            assert item.select_one("a"), ".p-item should contain an <a> tag"
            assert item.select_one(".p-item__name, [class*='name']"), (
                ".p-item should contain a name element"
            )

    def test_primary_mock_has_price(self):
        """Primary mock should include price elements matching [class*='price']."""
        soup = BeautifulSoup(MAPCAMERA_HTML, "html.parser")
        for item in soup.select(".p-item"):
            price_el = item.select_one("[class*='price']")
            assert price_el is not None, ".p-item should contain a price element"
            assert price_el.get_text(strip=True), "Price element should have text"

    def test_product_item_fallback_structure(self):
        """Fallback mock uses .product-item instead of .p-item."""
        soup = BeautifulSoup(MAPCAMERA_PRODUCT_ITEM_HTML, "html.parser")
        assert not soup.select(".p-item"), "Should NOT have .p-item"
        items = soup.select(".product-item")
        assert len(items) >= 1
        for item in items:
            assert item.select_one("a")
            assert item.select_one("[class*='name'], [class*='title'], h2, h3")

    def test_item_list_fallback_structure(self):
        """Fallback mock uses .item-list li instead of .p-item/.product-item."""
        soup = BeautifulSoup(MAPCAMERA_ITEM_LIST_HTML, "html.parser")
        assert not soup.select(".p-item"), "Should NOT have .p-item"
        assert not soup.select(".product-item"), "Should NOT have .product-item"
        items = soup.select(".item-list li")
        assert len(items) >= 1

    def test_link_fallback_has_no_container_selectors(self):
        """Link fallback mock should not match any container selector."""
        soup = BeautifulSoup(MAPCAMERA_LINK_FALLBACK_HTML, "html.parser")
        assert not soup.select(".p-item")
        assert not soup.select(".product-item")
        assert not soup.select(".item-list li")
        assert not soup.select("[class*='product']")
        # But DOES have item/product links
        links = soup.select("a[href*='/item/'], a[href*='/product/']")
        assert len(links) >= 1

    def test_mixed_mock_uses_same_primary_selector(self):
        """The filter-testing mock uses the same .p-item structure."""
        soup = BeautifulSoup(MAPCAMERA_MIXED_HTML, "html.parser")
        items = soup.select(".p-item")
        assert len(items) >= 2
