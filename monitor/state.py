"""State persistence for deduplication of seen listings."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Prune entries older than 30 days
MAX_AGE_SECONDS = 30 * 24 * 60 * 60


class StateManager:
    """Track seen listing URLs in a JSON file to avoid duplicate notifications."""

    def __init__(self, state_path: str = "data/state.json") -> None:
        self.path = Path(state_path)
        self.seen: dict[str, float] = {}  # url -> timestamp
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                self.seen = data.get("seen", {})
                logger.info("Loaded %d seen listings from state", len(self.seen))
            except Exception:
                logger.exception("Failed to load state file, starting fresh")
                self.seen = {}
        else:
            logger.info("No state file found, starting fresh")

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"seen": self.seen}, indent=2))

    def is_new(self, url: str) -> bool:
        return url not in self.seen

    def mark_seen(self, url: str) -> None:
        self.seen[url] = time.time()
        self._save()

    def prune(self) -> None:
        now = time.time()
        before = len(self.seen)
        self.seen = {url: ts for url, ts in self.seen.items() if now - ts < MAX_AGE_SECONDS}
        pruned = before - len(self.seen)
        if pruned:
            logger.info("Pruned %d old entries from state", pruned)
            self._save()
