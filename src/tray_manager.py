"""
PromptEnhancer — System tray icon and menu manager.

Uses pystray for the system tray icon with right-click menu including
enhancement styles, settings access, history, and exit.
"""

import logging
import os
import threading

import pystray
from PIL import Image, ImageDraw, ImageFont

from .constants import ENHANCEMENT_STYLES, ICON_PATH

logger = logging.getLogger(__name__)


class TrayManager:
    """Manages the system tray icon and context menu."""

    def __init__(
        self,
        on_settings=None,
        on_history=None,
        on_enhance_now=None,
        on_style_change=None,
        on_exit=None,
        get_current_style=None,
    ):
        """
        Args:
            on_settings: Callback when "Settings" is clicked.
            on_history: Callback when "History" is clicked.
            on_enhance_now: Callback when "Enhance Now" is clicked.
            on_style_change: Callback(style_key) when style is changed.
            on_exit: Callback when "Exit" is clicked.
            get_current_style: Callable that returns the current style key.
        """
        self._on_settings = on_settings
        self._on_history = on_history
        self._on_enhance_now = on_enhance_now
        self._on_style_change = on_style_change
        self._on_exit = on_exit
        self._get_current_style = get_current_style
        self._icon = None
        self._thread = None

    def _load_icon(self) -> Image.Image:
        """Load the app icon, or generate a fallback."""
        if os.path.exists(ICON_PATH):
            try:
                return Image.open(ICON_PATH)
            except Exception as e:
                logger.warning(f"Failed to load icon: {e}")

        # Generate a fallback icon programmatically
        return self._generate_fallback_icon()

    def _generate_fallback_icon(self) -> Image.Image:
        """Generate a simple fallback icon with 'PE' text."""
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gradient-like background (rounded rectangle approximation)
        draw.rounded_rectangle(
            [2, 2, size - 2, size - 2],
            radius=12,
            fill=(99, 102, 241),  # Indigo-500
        )

        # Draw "PE" text
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except Exception:
            font = ImageFont.load_default()

        # Center the text
        text = "PE"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (size - tw) // 2
        y = (size - th) // 2 - 2
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        return img

    def _is_style_checked(self, style_key: str):
        """Return a callable that checks if a style is the current one."""
        def check(item):
            if self._get_current_style:
                return self._get_current_style() == style_key
            return style_key == "standard"
        return check

    def _on_style_click(self, style_key: str):
        """Return a callback for when a style menu item is clicked."""
        def callback(icon, item):
            if self._on_style_change:
                self._on_style_change(style_key)
        return callback

    def _build_menu(self) -> pystray.Menu:
        """Build the right-click context menu."""

        # Style submenu items
        style_items = []
        for key, style in ENHANCEMENT_STYLES.items():
            style_items.append(
                pystray.MenuItem(
                    f"{style['icon']} {style['name']}",
                    self._on_style_click(key),
                    checked=self._is_style_checked(key),
                    radio=True,
                )
            )

        menu = pystray.Menu(
            pystray.MenuItem(
                "✨ Enhance Now",
                lambda icon, item: self._on_enhance_now() if self._on_enhance_now else None,
                default=True,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⚙ Settings",
                lambda icon, item: self._on_settings() if self._on_settings else None,
            ),
            pystray.MenuItem(
                "📋 History",
                lambda icon, item: self._on_history() if self._on_history else None,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Style",
                pystray.Menu(*style_items),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "❌ Exit",
                lambda icon, item: self._handle_exit(icon),
            ),
        )

        return menu

    def _handle_exit(self, icon):
        """Handle the exit action."""
        icon.stop()
        if self._on_exit:
            self._on_exit()

    def run(self):
        """Start the system tray icon (blocking — call from main thread or dedicated thread)."""
        image = self._load_icon()
        menu = self._build_menu()

        self._icon = pystray.Icon(
            "PromptEnhancer",
            image,
            "PromptEnhancer — Ctrl+Shift+E to enhance",
            menu,
        )

        logger.info("System tray icon starting.")
        self._icon.run()

    def run_in_thread(self):
        """Start the system tray in a background thread."""
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the system tray icon."""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def update_tooltip(self, text: str):
        """Update the tray icon tooltip text."""
        if self._icon:
            self._icon.title = text
