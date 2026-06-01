"""
PromptEnhancer — Clipboard manager with full format preservation.

Uses win32clipboard (pywin32) to save and restore ALL clipboard formats
(text, images, rich text, etc.) so the user's clipboard is never disrupted.
Uses the `keyboard` library to simulate Ctrl+C and Ctrl+V.
"""

import logging
import time

import keyboard
import win32clipboard
import win32con

logger = logging.getLogger(__name__)


class ClipboardManager:
    """Manages clipboard operations with full format preservation."""

    def __init__(self):
        self._retry_count = 3
        self._retry_delay = 0.05  # 50ms between retries

    # ── Low-Level Clipboard Operations ───────────────────────────────────

    def _open_clipboard(self):
        """Open the clipboard with retries (it may be locked by another app)."""
        for attempt in range(self._retry_count):
            try:
                win32clipboard.OpenClipboard()
                return True
            except Exception:
                if attempt < self._retry_count - 1:
                    time.sleep(self._retry_delay)
        logger.error("Failed to open clipboard after retries.")
        return False

    def _close_clipboard(self):
        """Safely close the clipboard."""
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass

    def save_clipboard(self) -> dict:
        """
        Save ALL clipboard formats to a dictionary.
        Returns {format_id: data} for every available format.
        """
        saved = {}
        if not self._open_clipboard():
            return saved

        try:
            fmt = win32clipboard.EnumClipboardFormats(0)
            while fmt != 0:
                try:
                    data = win32clipboard.GetClipboardData(fmt)
                    saved[fmt] = data
                except Exception:
                    # Some formats (e.g., synthesized) can't be read
                    pass
                fmt = win32clipboard.EnumClipboardFormats(fmt)
        except Exception as e:
            logger.warning(f"Error saving clipboard: {e}")
        finally:
            self._close_clipboard()

        return saved

    def restore_clipboard(self, saved: dict):
        """
        Restore ALL clipboard formats from a previously saved dictionary.
        """
        if not saved:
            return

        if not self._open_clipboard():
            return

        try:
            win32clipboard.EmptyClipboard()
            for fmt, data in saved.items():
                try:
                    win32clipboard.SetClipboardData(fmt, data)
                except Exception:
                    # Some formats can't be restored (synthesized by the OS)
                    pass
        except Exception as e:
            logger.warning(f"Error restoring clipboard: {e}")
        finally:
            self._close_clipboard()

    def get_clipboard_text(self) -> str:
        """Read plain text from the clipboard."""
        if not self._open_clipboard():
            return ""

        try:
            if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
                return data if isinstance(data, str) else ""
            return ""
        except Exception as e:
            logger.warning(f"Error reading clipboard text: {e}")
            return ""
        finally:
            self._close_clipboard()

    def set_clipboard_text(self, text: str):
        """Write plain text to the clipboard."""
        if not self._open_clipboard():
            return

        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        except Exception as e:
            logger.warning(f"Error setting clipboard text: {e}")
        finally:
            self._close_clipboard()

    # ── High-Level Operations ────────────────────────────────────────────

    def get_selected_text(self) -> str:
        """
        Capture the currently selected text from ANY application.
        
        Flow:
        1. Save current clipboard state
        2. Simulate Ctrl+C to copy selection
        3. Read the copied text
        4. Restore original clipboard state
        5. Return the selected text
        """
        # Save the current clipboard
        saved = self.save_clipboard()

        # Small delay to ensure focus is stable
        time.sleep(0.05)

        # Simulate Ctrl+C
        keyboard.send("ctrl+c")

        # Wait for the copy to complete
        time.sleep(0.15)

        # Read what was copied
        text = self.get_clipboard_text()

        # Restore original clipboard
        self.restore_clipboard(saved)

        return text.strip() if text else ""

    def paste_text(self, text: str):
        """
        Paste text into the currently focused application.
        
        Flow:
        1. Save current clipboard state
        2. Set clipboard to our text
        3. Simulate Ctrl+V
        4. Wait for paste to complete
        5. Restore original clipboard state
        """
        # Save the current clipboard
        saved = self.save_clipboard()

        # Set our text
        self.set_clipboard_text(text)

        # Small delay before pasting
        time.sleep(0.05)

        # Simulate Ctrl+V
        keyboard.send("ctrl+v")

        # Wait for the paste to complete
        time.sleep(0.15)

        # Restore original clipboard
        self.restore_clipboard(saved)
