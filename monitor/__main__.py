"""CLI entry point for python -m monitor."""

import logging

from monitor.cli import run
from monitor.config import get_config

logger = logging.getLogger(__name__)


def main():
    """Main entry point when running as module."""
    logger.info("Initializing monitor...")
    config = get_config()
    run(config)


if __name__ == "__main__":
    main()
