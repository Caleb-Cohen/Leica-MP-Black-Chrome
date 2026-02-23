"""Configuration loader for the monitor."""

import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

logger = logging.getLogger(__name__)


def get_config() -> dict[str, Any]:
    """Load configuration from .env file and return as dictionary."""
    # Load .env file if python-dotenv is available
    env_path = Path(".env")
    if load_dotenv:
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded configuration from .env file")
        else:
            logger.info("No .env file found, using environment variables")
    else:
        logger.warning("python-dotenv not installed, using environment variables only")

    config: dict[str, Any] = {}

    # Discord webhook URL (required)
    config["discord_webhook_url"] = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not config["discord_webhook_url"]:
        logger.error("DISCORD_WEBHOOK_URL is required but not set")
        sys.exit(1)

    # Discord user ID to tag on match (required)
    config["discord_user_id"] = os.getenv("DISCORD_USER_ID", "")
    if not config["discord_user_id"]:
        logger.error("DISCORD_USER_ID is required but not set")
        sys.exit(1)

    # Poll interval in seconds (default: 5 minutes)
    config["poll_interval_seconds"] = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))

    return config
