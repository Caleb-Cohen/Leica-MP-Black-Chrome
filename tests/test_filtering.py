"""Tests for the Leica MP Black Chrome filtering logic."""

import pytest

from monitor.filtering import is_black_chrome
from monitor.scrapers.base import Listing


def _listing(title: str) -> Listing:
    return Listing(title=title, url="https://example.com", price=None, source="test")


class TestIsBlackChrome:
    """Verify is_black_chrome accepts correct listings and rejects others."""

    # --- should accept ---

    def test_accepts_black_chrome(self):
        assert is_black_chrome(_listing("Leica MP 0.72 Black Chrome"))

    def test_accepts_blk_chrome(self):
        assert is_black_chrome(_listing("Leica MP Blk Chrome"))

    def test_accepts_chrome_without_paint(self):
        assert is_black_chrome(_listing("Leica MP Chrome"))

    def test_accepts_bare_leica_mp(self):
        assert is_black_chrome(_listing("Leica MP"))

    def test_accepts_case_insensitive(self):
        assert is_black_chrome(_listing("LEICA MP BLACK CHROME"))

    def test_accepts_leica_mp_with_viewfinder(self):
        assert is_black_chrome(_listing("Leica MP 0.72 Black Chrome Rangefinder"))

    # --- should reject ---

    def test_rejects_black_paint(self):
        assert not is_black_chrome(_listing("Leica MP Black Paint"))

    def test_rejects_m_p_digital(self):
        assert not is_black_chrome(_listing("Leica M-P (Typ 240)"))

    def test_rejects_mp_240(self):
        assert not is_black_chrome(_listing("Leica MP-240 Digital"))

    def test_rejects_mp_typ(self):
        assert not is_black_chrome(_listing("Leica MP typ 240"))

    def test_rejects_non_leica(self):
        assert not is_black_chrome(_listing("Nikon MP Black Chrome"))

    def test_rejects_mp_in_word(self):
        assert not is_black_chrome(_listing("Big lamp post"))

    def test_rejects_no_mp(self):
        assert not is_black_chrome(_listing("Leica M6 Black Chrome"))


class TestFilterIntegration:
    """Verify filtering a batch of mixed listings returns only matches."""

    @pytest.fixture
    def mixed_listings(self):
        return [
            Listing(
                title="Leica MP 0.72 Black Chrome",
                url="https://example.com/1",
                price="$5295",
                source="test",
            ),
            Listing(
                title="Leica M-P (Typ 240)",
                url="https://example.com/2",
                price="$3500",
                source="test",
            ),
            Listing(
                title="Leica MP Black Paint",
                url="https://example.com/3",
                price="$8000",
                source="test",
            ),
            Listing(
                title="Leica MP 0.58 Chrome",
                url="https://example.com/4",
                price="$5295",
                source="test",
            ),
            Listing(
                title="Canon EOS R5",
                url="https://example.com/5",
                price="$3899",
                source="test",
            ),
        ]

    def test_filter_returns_only_matches(self, mixed_listings):
        matches = [listing for listing in mixed_listings if is_black_chrome(listing)]
        assert len(matches) == 2
        assert matches[0].title == "Leica MP 0.72 Black Chrome"
        assert matches[1].title == "Leica MP 0.58 Chrome"
