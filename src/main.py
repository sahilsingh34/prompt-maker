"""
PromptEnhancer — Main entry point and application orchestrator.

Initializes all modules, handles single-instance enforcement,
logging setup, and coordinates the system tray + hotkey lifecycle.
"""

import ctypes
import logging
import logging.handlers
import os
import sys
import threading

# ── Single Instance Mutex ────────────────────────────────────────────────────
# Must be checked BEFORE doing anything else.

def _ensure_single_instance():
    """Prevent multiple instances using a Windows mutex."""
    mutex_name = "PromptEnhancer_SingleInstance_Mutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()

    if last_error == 183:  # ERROR_ALREADY_EXISTS
        # Another instance is running
        ctypes.windll.user32.MessageBoxW(
            0,
            "PromptEnhancer is already running.\n\n"
            "Check the system tray (notification area).",
            "PromptEnhancer",
            0x40,  # MB_ICONINFORMATION
        )
        sys.exit(0)

    return mutex  # Keep reference to prevent GC


# ── Logging Setup ────────────────────────────────────────────────────────────

def _setup_logging():
    """Configure application logging with rotation."""
    from .constants import APPDATA_DIR, LOG_FILE

    os.makedirs(APPDATA_DIR, exist_ok=True)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # File handler with rotation (5MB max, 3 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root_logger.addHandler(file_handler)

    # Console handler (for development)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    )
    root_logger.addHandler(console_handler)

    return root_logger


# ── Main Application ─────────────────────────────────────────────────────────

class PromptEnhancerApp:
    """Main application orchestrator."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("PromptEnhancer starting up...")

        # Initialize all managers
        self._init_config()
        self._init_notification()
        self._init_history()
        self._init_enhancer()
        self._init_clipboard()
        self._init_hotkey()
        self._init_settings_window()
        self._init_tray()

        self.logger.info("All modules initialized.")

    def _init_config(self):
        """Initialize configuration manager."""
        from .config_manager import ConfigManager

        self.config = ConfigManager()
        self.logger.info(f"Config loaded. Style: {self.config.enhancement_style}")

    def _init_notification(self):
        """Initialize notification manager."""
        from .notification_manager import NotificationManager

        self.notifier = NotificationManager()

    def _init_history(self):
        """Initialize history manager."""
        from .history_manager import HistoryManager

        self.history = HistoryManager()
        self.logger.info(f"History loaded: {self.history.count} entries.")

    def _init_enhancer(self):
        """Initialize the prompt enhancer (API client)."""
        from .enhancer import PromptEnhancer

        self.enhancer = PromptEnhancer(
            api_key=self.config.get_api_key(),
            model=self.config.model,
        )

    def _init_clipboard(self):
        """Initialize clipboard manager."""
        from .clipboard_manager import ClipboardManager

        self.clipboard = ClipboardManager()

    def _init_hotkey(self):
        """Initialize and register the global hotkey."""
        from .hotkey_manager import HotkeyManager

        self.hotkey_mgr = HotkeyManager(
            clipboard=self.clipboard,
            enhancer=self.enhancer,
            notifier=self.notifier,
            history=self.history,
            hotkey=self.config.hotkey,
            style_getter=lambda: self.config.enhancement_style,
        )
        self.hotkey_mgr.register()

    def _init_settings_window(self):
        """Initialize the settings window (lazy — created on demand)."""
        from .settings_window import SettingsWindow

        self.settings_win = SettingsWindow(
            config=self.config,
            enhancer=self.enhancer,
            on_hotkey_changed=self._on_hotkey_changed,
            on_style_changed=self._on_style_changed,
            on_save=self._on_settings_saved,
        )

    def _init_tray(self):
        """Initialize the system tray manager."""
        from .tray_manager import TrayManager

        self.tray = TrayManager(
            on_settings=self._open_settings,
            on_history=self._open_history,
            on_enhance_now=self._enhance_now,
            on_style_change=self._on_tray_style_change,
            on_exit=self._exit,
            get_current_style=lambda: self.config.enhancement_style,
        )

    # ── Callbacks ────────────────────────────────────────────────────────

    def _open_settings(self):
        """Open the settings window (from tray menu)."""
        # Settings uses customtkinter which needs to run on the main tkinter thread.
        # We create a new tkinter root if needed.
        self._run_in_tk_thread(lambda: self.settings_win.show())

    def _open_history(self):
        """Open the history window."""
        from .settings_window import HistoryWindow

        def show():
            hw = HistoryWindow(
                history_data=self.history.get_all(),
                on_clear=self._clear_history,
            )
            hw.show()

        self._run_in_tk_thread(show)

    def _clear_history(self):
        """Clear all history."""
        self.history.clear()

    def _enhance_now(self):
        """Manually trigger enhancement (from tray menu)."""
        self.hotkey_mgr.trigger_manually()

    def _on_tray_style_change(self, style_key: str):
        """Handle style change from tray menu."""
        self.config.enhancement_style = style_key
        self.config.save()
        from .constants import ENHANCEMENT_STYLES, MSG_STYLE_CHANGED

        style_name = ENHANCEMENT_STYLES.get(style_key, {}).get("name", style_key)
        self.notifier.show_info(MSG_STYLE_CHANGED.format(style=style_name))

    def _on_hotkey_changed(self, new_hotkey: str):
        """Handle hotkey change from settings."""
        self.hotkey_mgr.update_hotkey(new_hotkey)

    def _on_style_changed(self, new_style: str):
        """Handle style change from settings."""
        self.logger.info(f"Style changed to: {new_style}")

    def _on_settings_saved(self):
        """Handle settings save."""
        self.logger.info("Settings saved from UI.")

    def _exit(self):
        """Clean shutdown."""
        self.logger.info("Shutting down...")
        try:
            self.hotkey_mgr.unregister()
        except Exception:
            pass
        try:
            self.tray.stop()
        except Exception:
            pass
        self.logger.info("Goodbye!")
        os._exit(0)

    # ── Tkinter Thread Helper ────────────────────────────────────────────

    def _run_in_tk_thread(self, callback):
        """
        Run a callback that creates a tkinter/customtkinter window.
        CustomTkinter needs a root window; we create one if needed.
        """
        import customtkinter as ctk

        def run():
            # Check if a root window already exists
            try:
                root = ctk.CTk()
                root.withdraw()  # Hidden root
                callback()
                root.mainloop()
            except Exception as e:
                self.logger.error(f"Tkinter thread error: {e}", exc_info=True)

        t = threading.Thread(target=run, daemon=True)
        t.start()

    # ── Run ──────────────────────────────────────────────────────────────

    def run(self):
        """Start the application. Blocks until exit."""
        # Check if first run — open settings immediately
        if self.config.first_run or not self.config.has_api_key():
            self.logger.info("First run detected. Opening settings...")
            self._open_settings()

        # Start the system tray icon (blocking call)
        self.logger.info("Starting system tray...")
        self.tray.run()


# ── Entry Point ──────────────────────────────────────────────────────────────

def main():
    """Application entry point."""
    # Single instance check
    mutex = _ensure_single_instance()

    # Setup logging
    logger = _setup_logging()

    try:
        app = PromptEnhancerApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        ctypes.windll.user32.MessageBoxW(
            0,
            f"PromptEnhancer encountered a fatal error:\n\n{str(e)}\n\n"
            "Check the log file for details.",
            "PromptEnhancer Error",
            0x10,  # MB_ICONERROR
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
