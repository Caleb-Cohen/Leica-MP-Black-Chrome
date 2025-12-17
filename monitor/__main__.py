"""CLI entry point for python -m monitor."""

import logging

from monitor.cli import run
from monitor.config import get_config

logger = logging.getLogger(__name__)


def main():
    """Main entry point when running as module."""
    # Initialize logging (already configured in __init__.py)
    logger.info("Initializing monitor...")

    # Load configuration
    # TODO Phase 1+: Use config values for poll interval, etc.
    config = get_config()
    logger.debug(f"Loaded config: {config}")

    # Run the monitor
    # TODO Phase 1: Add polling loop with configurable interval
    # TODO Phase 2: Add state management initialization
    # TODO Phase 3: Add Discord webhook initialization
    run()


if __name__ == "__main__":
    main()
