"""Configuration loader for the monitor."""

import logging
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

logger = logging.getLogger(__name__)


def get_config() -> dict[str, Any]:
    """
    Load configuration from .env file and return as dictionary.

    Returns:
        Dictionary of configuration values with defaults.
    """
    config = {}

    # Load .env file if python-dotenv is available
    env_path = Path(".env")
    if load_dotenv:
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded configuration from .env file")
        else:
            logger.warning(".env file not found, using defaults")
    else:
        logger.warning("python-dotenv not installed, using environment variables only")

    # TODO Phase 1: Add POLL_INTERVAL_SECONDS config
    # config["poll_interval_seconds"] = int(os.getenv("POLL_INTERVAL_SECONDS", "600"))

    # TODO Phase 2: Add STATE_FILE_PATH config
    # config["state_file_path"] = os.getenv("STATE_FILE_PATH", "state.json")

    # TODO Phase 3: Add DISCORD_WEBHOOK_URL config
    # config["discord_webhook_url"] = os.getenv("DISCORD_WEBHOOK_URL", "")

    return config
