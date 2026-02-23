"""Filtering logic to identify Leica MP Black Chrome listings."""

from __future__ import annotations

import re

from monitor.scrapers.base import Listing


def is_black_chrome(listing: Listing) -> bool:
    """Check if a listing is for a Leica MP Black Chrome (not Black Paint, not M-P digital)."""
    title = listing.title.lower()

    # Reject Leica M-P (digital rangefinder) - hyphenated is a different camera
    if re.search(r"\bm[\s-]?p\b", title) and "-" in re.findall(r"m[\s-]?p", title)[0]:
        return False

    # Must mention "leica"
    if "leica" not in title:
        return False

    # Must mention "mp" as a word (not part of another word like "lamp")
    if not re.search(r"\bmp\b", title):
        return False

    # Reject black paint explicitly
    if "black paint" in title:
        return False

    # Reject known digital models that might slip through
    if re.search(r"\bmp[\s-]?(240|typ)", title):
        return False

    # Must indicate chrome/black chrome
    # Accept: "black chrome", "chrome", "blk chrome"
    # Also accept listings that just say "Leica MP" without specifying paint
    # (the MP Black Chrome is the standard/common finish)
    if "black chrome" in title or "blk chrome" in title:
        return True

    # If it says "chrome" without "paint", it's likely black chrome
    if "chrome" in title and "paint" not in title:
        return True

    # If it just says "Leica MP" with no finish specified, still include it
    # as it's likely the standard black chrome finish - user can verify
    return "paint" not in title
