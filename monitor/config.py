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

    required = [
        "DISCORD_WEBHOOK_URL",
        "DISCORD_USER_ID",
        "POLL_INTERVAL_SECONDS",
        "CAMERAWEST_SEARCH_URL",
        "CAMERAWEST_SEARCH_QUERY",
        "CAMERAWEST_BASE_URL",
        "MAPCAMERA_SEARCH_URL",
        "MAPCAMERA_SEARCH_KEYWORD",
        "MAPCAMERA_BASE_URL",
        "FREDMIRANDA_FORUM_URL",
        "FREDMIRANDA_BASE_URL",
    ]

    missing = [key for key in required if not os.getenv(key)]
    if missing:
        for key in missing:
            logger.error("Missing required env var: %s", key)
        sys.exit(1)

    return {
        "discord_webhook_url": os.environ["DISCORD_WEBHOOK_URL"],
        "discord_user_id": os.environ["DISCORD_USER_ID"],
        "poll_interval_seconds": int(os.environ["POLL_INTERVAL_SECONDS"]),
        "camerawest_search_url": os.environ["CAMERAWEST_SEARCH_URL"],
        "camerawest_search_query": os.environ["CAMERAWEST_SEARCH_QUERY"],
        "camerawest_base_url": os.environ["CAMERAWEST_BASE_URL"],
        "mapcamera_search_url": os.environ["MAPCAMERA_SEARCH_URL"],
        "mapcamera_search_keyword": os.environ["MAPCAMERA_SEARCH_KEYWORD"],
        "mapcamera_base_url": os.environ["MAPCAMERA_BASE_URL"],
        "fredmiranda_forum_url": os.environ["FREDMIRANDA_FORUM_URL"],
        "fredmiranda_base_url": os.environ["FREDMIRANDA_BASE_URL"],
    }
