"""Discord webhook integration for notifications."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime

import httpx

from monitor.scrapers.base import Listing

logger = logging.getLogger(__name__)

# Green for alerts, gray for status
COLOR_ALERT = 0x00FF00
COLOR_STATUS = 0x808080
COLOR_ERROR = 0xFF0000


class DiscordNotifier:
    """Send notifications to Discord via webhook."""

    def __init__(self, webhook_url: str, user_id: str) -> None:
        self.webhook_url = webhook_url
        self.user_id = user_id
        self.client = httpx.Client(timeout=30.0)

    def _post(self, payload: dict) -> None:
        for attempt in range(3):
            try:
                resp = self.client.post(self.webhook_url, json=payload)
                if resp.status_code == 429:
                    retry_after = resp.json().get("retry_after", 5)
                    logger.warning("Discord rate limited, waiting %ss", retry_after)
                    time.sleep(retry_after)
                    continue
                resp.raise_for_status()
                return
            except Exception:
                if attempt == 2:
                    logger.exception("Failed to send Discord message after 3 attempts")
                else:
                    time.sleep(2)

    def send_status(self, results: dict[str, int]) -> None:
        """Send a poll status update showing what was checked and match counts."""
        total = sum(results.values())
        fields = [
            {"name": source, "value": f"{count} match(es)", "inline": True}
            for source, count in results.items()
        ]

        payload = {
            "embeds": [
                {
                    "title": "Poll Complete",
                    "description": f"Checked {len(results)} sources — {total} new match(es)",
                    "color": COLOR_STATUS,
                    "fields": fields,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ]
        }
        self._post(payload)

    def send_alert(self, listing: Listing) -> None:
        """Send an alert for a new Leica MP Black Chrome listing, tagging the user."""
        fields = [{"name": "Source", "value": listing.source, "inline": True}]
        if listing.price:
            fields.append({"name": "Price", "value": listing.price, "inline": True})

        payload = {
            "content": f"<@{self.user_id}>",
            "embeds": [
                {
                    "title": "Leica MP Black Chrome Found!",
                    "description": listing.title,
                    "url": listing.url,
                    "color": COLOR_ALERT,
                    "fields": fields,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ],
        }
        self._post(payload)

    def send_error(self, message: str) -> None:
        """Send an error notification."""
        payload = {
            "embeds": [
                {
                    "title": "Monitor Error",
                    "description": message,
                    "color": COLOR_ERROR,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ]
        }
        self._post(payload)

    def close(self) -> None:
        self.client.close()
