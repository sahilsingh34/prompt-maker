"""
PromptEnhancer — Windows toast notification manager.

Uses `windows-toasts` for native WinRT toast notifications.
Falls back to a simple tkinter messagebox if toasts fail.
"""

import logging
import threading

logger = logging.getLogger(__name__)

# Try to import windows-toasts
_toasts_available = False
try:
    from windows_toasts import Toast, ToastDisplayImage, WindowsToaster
    _toasts_available = True
except ImportError:
    logger.warning("windows-toasts not available. Using fallback notifications.")


class NotificationManager:
    """Non-blocking Windows toast notifications."""

    def __init__(self, app_name: str = "PromptEnhancer"):
        self._app_name = app_name
        self._toaster = None

        if _toasts_available:
            try:
                self._toaster = WindowsToaster(self._app_name)
                logger.info("Windows toast notifications initialized.")
            except Exception as e:
                logger.warning(f"Failed to init toaster: {e}")
                self._toaster = None

    def _show_toast(self, title: str, message: str):
        """Show a toast notification (runs in worker thread)."""
        if self._toaster:
            try:
                toast = Toast()
                toast.text_fields = [title, message]
                self._toaster.show_toast(toast)
                return
            except Exception as e:
                logger.warning(f"Toast failed: {e}")

        # Fallback: print to console
        logger.info(f"[Notification] {title}: {message}")

    def _show_async(self, title: str, message: str):
        """Show notification in a background thread (non-blocking)."""
        t = threading.Thread(target=self._show_toast, args=(title, message), daemon=True)
        t.start()

    def show_success(self, message: str):
        """Show a success notification."""
        self._show_async("PromptEnhancer", message)

    def show_error(self, message: str):
        """Show an error notification."""
        self._show_async("PromptEnhancer", message)

    def show_info(self, message: str):
        """Show an informational notification."""
        self._show_async("PromptEnhancer", message)
