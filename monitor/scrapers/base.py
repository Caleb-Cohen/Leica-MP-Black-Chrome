"""Scraper base classes and data models."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
}


@dataclass
class Listing:
    """A single product or forum listing."""

    title: str
    url: str
    price: str | None
    source: str


class BaseScraper(ABC):
    """Base class for all site scrapers."""

    name: str = "unknown"

    def __init__(self, config: dict) -> None:
        self.config = config
        self.client = httpx.Client(
            headers=DEFAULT_HEADERS,
            timeout=httpx.Timeout(connect=30.0, read=60.0, write=30.0, pool=30.0),
            follow_redirects=True,
        )

    @abstractmethod
    def scrape(self) -> list[Listing]:
        """Scrape the site and return raw listings (before filtering)."""

    def close(self) -> None:
        self.client.close()
