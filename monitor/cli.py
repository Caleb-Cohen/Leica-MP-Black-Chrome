"""Main monitor loop."""

import logging
import time
from typing import Any

from monitor.discord import DiscordNotifier
from monitor.filtering import is_black_chrome
from monitor.scrapers import CameraWestScraper, FredMirandaScraper
from monitor.state import StateManager

logger = logging.getLogger(__name__)


def run(config: dict[str, Any]) -> None:
    """Main polling loop — scrape, filter, notify, repeat."""
    interval = config["poll_interval_seconds"]

    notifier = DiscordNotifier(
        webhook_url=config["discord_webhook_url"],
        user_id=config["discord_user_id"],
    )
    state = StateManager()

    scrapers = [
        CameraWestScraper(config),
        FredMirandaScraper(config),
        # MapCamera excluded — blocked by Akamai Bot Manager.
        # Re-enable once a bypass strategy is confirmed working.
    ]

    logger.info("Starting monitor — polling every %ds", interval)
    logger.info("Active scrapers: %s", [s.name for s in scrapers])

    try:
        while True:
            results: dict[str, int] = {}

            for scraper in scrapers:
                try:
                    raw = scraper.scrape()
                    matches = [listing for listing in raw if is_black_chrome(listing)]
                    new = [listing for listing in matches if state.is_new(listing.url)]

                    results[scraper.name] = len(new)

                    for listing in new:
                        logger.info("NEW: %s — %s", listing.title, listing.url)
                        notifier.send_alert(listing)
                        state.mark_seen(listing.url)

                except Exception:
                    logger.exception("Error scraping %s", scraper.name)
                    results[scraper.name] = 0

            # Status update every cycle
            notifier.send_status(results)

            # Prune old state entries periodically
            state.prune()

            logger.info("Sleeping %ds until next poll...", interval)
            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        for scraper in scrapers:
            scraper.close()
        notifier.close()
