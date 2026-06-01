"""
PromptEnhancer — Global hotkey manager.

Registers a system-wide keyboard shortcut and orchestrates the
text capture → enhance → paste workflow.
"""

import logging
import threading
import time

import keyboard

from .clipboard_manager import ClipboardManager
from .constants import (
    MAX_TEXT_LENGTH,
    MSG_ENHANCING,
    MSG_INVALID_KEY,
    MSG_NO_INTERNET,
    MSG_NO_TEXT,
    MSG_RATE_LIMIT,
    MSG_SUCCESS,
    MSG_TEXT_TOO_LONG,
    MSG_TIMEOUT,
    MSG_UNKNOWN_ERROR,
)
from .enhancer import (
    InvalidAPIKeyError,
    NetworkError,
    PromptEnhancer,
    RateLimitError,
    TimeoutError,
)
from .history_manager import HistoryManager
from .notification_manager import NotificationManager

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey registration and the enhancement workflow."""

    def __init__(
        self,
        clipboard: ClipboardManager,
        enhancer: PromptEnhancer,
        notifier: NotificationManager,
        history: HistoryManager,
        hotkey: str = "ctrl+shift+e",
        style_getter=None,
    ):
        self._clipboard = clipboard
        self._enhancer = enhancer
        self._notifier = notifier
        self._history = history
        self._hotkey = hotkey
        self._style_getter = style_getter  # callable that returns current style
        self._is_processing = False
        self._lock = threading.Lock()
        self._registered = False

    def register(self):
        """Register the global hotkey."""
        try:
            keyboard.add_hotkey(self._hotkey, self._on_trigger, suppress=True)
            self._registered = True
            logger.info(f"Hotkey registered: {self._hotkey}")
        except Exception as e:
            logger.error(f"Failed to register hotkey '{self._hotkey}': {e}")

    def unregister(self):
        """Unregister the global hotkey."""
        try:
            if self._registered:
                keyboard.remove_hotkey(self._hotkey)
                self._registered = False
                logger.info(f"Hotkey unregistered: {self._hotkey}")
        except Exception as e:
            logger.warning(f"Error unregistering hotkey: {e}")

    def update_hotkey(self, new_hotkey: str):
        """Change the registered hotkey."""
        self.unregister()
        self._hotkey = new_hotkey
        self.register()

    def _on_trigger(self):
        """
        Called when the hotkey is pressed.
        Spawns the enhancement workflow in a separate thread to avoid
        blocking the keyboard hook.
        """
        # Debounce: ignore if already processing
        if not self._lock.acquire(blocking=False):
            return

        try:
            if self._is_processing:
                return
            self._is_processing = True
        finally:
            self._lock.release()

        # Run enhancement in background thread
        t = threading.Thread(target=self._enhance_workflow, daemon=True)
        t.start()

    def _enhance_workflow(self):
        """
        The full enhancement workflow:
        1. Capture selected text
        2. Validate
        3. Enhance via API
        4. Paste back
        5. Notify
        """
        try:
            # Small delay to let the hotkey release complete
            time.sleep(0.1)

            # Step 1: Capture selected text
            text = self._clipboard.get_selected_text()

            # Step 2: Validate
            if not text:
                self._notifier.show_error(MSG_NO_TEXT)
                return

            if len(text) > MAX_TEXT_LENGTH:
                self._notifier.show_error(MSG_TEXT_TOO_LONG)
                return

            # Step 3: Show "enhancing" notification
            self._notifier.show_info(MSG_ENHANCING)

            # Get current style
            style = "standard"
            if self._style_getter:
                style = self._style_getter()

            # Step 4: Enhance via API
            enhanced = self._enhancer.enhance(text, style=style)

            if not enhanced:
                self._notifier.show_error(MSG_UNKNOWN_ERROR)
                return

            # Step 5: Paste enhanced text back
            self._clipboard.paste_text(enhanced)

            # Step 6: Success notification
            self._notifier.show_success(MSG_SUCCESS)

            # Step 7: Log to history
            try:
                self._history.add(text, enhanced, style)
            except Exception as e:
                logger.warning(f"Failed to log to history: {e}")

        except InvalidAPIKeyError:
            self._notifier.show_error(MSG_INVALID_KEY)
        except RateLimitError:
            self._notifier.show_error(MSG_RATE_LIMIT)
        except NetworkError:
            self._notifier.show_error(MSG_NO_INTERNET)
        except TimeoutError:
            self._notifier.show_error(MSG_TIMEOUT)
        except Exception as e:
            logger.error(f"Enhancement workflow error: {e}", exc_info=True)
            self._notifier.show_error(MSG_UNKNOWN_ERROR)
        finally:
            self._is_processing = False

    def trigger_manually(self):
        """Trigger enhancement manually (from tray menu)."""
        self._on_trigger()
