"""CLI interface for the monitor."""

import logging

logger = logging.getLogger(__name__)


def run():
    """
    Main entry point for the monitor.
    
    TODO Phase 1: Implement scraper to poll retailer pages
    TODO Phase 2: Add state persistence and deduplication
    TODO Phase 3: Add Discord webhook notifications
    TODO Phase 4: Add second retailer and shared abstractions
    TODO Phase 5: Add Docker deployment configuration
    """
    logger.info("Starting monitor...")
    logger.info("Monitor running (placeholder)")
    logger.info("Monitor stopped")

