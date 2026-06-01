"""
PromptEnhancer — Enhancement history manager.

Stores the last N enhanced prompts in a JSON file at %APPDATA%/PromptEnhancer/.
"""

import json
import logging
import os
from datetime import datetime

from .constants import HISTORY_FILE, MAX_HISTORY_SIZE

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages the enhancement history stored as JSON."""

    def __init__(self):
        self._history: list[dict] = []
        self.load()

    def load(self):
        """Load history from disk."""
        if not os.path.exists(HISTORY_FILE):
            self._history = []
            return

        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self._history = json.load(f)
            logger.info(f"Loaded {len(self._history)} history entries.")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load history: {e}")
            self._history = []

    def save(self):
        """Persist history to disk."""
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save history: {e}")

    def add(self, original: str, enhanced: str, style: str):
        """Add a new entry to the history (prepend, trim to max size)."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "original": original,
            "enhanced": enhanced,
            "style": style,
        }
        self._history.insert(0, entry)

        # Trim to max size
        if len(self._history) > MAX_HISTORY_SIZE:
            self._history = self._history[:MAX_HISTORY_SIZE]

        self.save()
        logger.info("History entry added.")

    def get_all(self) -> list[dict]:
        """Return all history entries."""
        return list(self._history)

    def clear(self):
        """Clear all history."""
        self._history = []
        self.save()
        logger.info("History cleared.")

    @property
    def count(self) -> int:
        """Number of history entries."""
        return len(self._history)
