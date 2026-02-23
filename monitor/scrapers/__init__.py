"""Scraper exports."""

from monitor.scrapers.base import BaseScraper, Listing
from monitor.scrapers.camerawest import CameraWestScraper
from monitor.scrapers.fredmiranda import FredMirandaScraper
from monitor.scrapers.mapcamera import MapCameraScraper

__all__ = [
    "BaseScraper",
    "CameraWestScraper",
    "FredMirandaScraper",
    "Listing",
    "MapCameraScraper",
]
