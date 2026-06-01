"""
PromptEnhancer — Settings window using CustomTkinter.

Modern, dark-mode-aware settings UI with tabbed interface for
API key, enhancement style, hotkey configuration, and general settings.
"""

import logging
import threading
import webbrowser

import customtkinter as ctk

from .config_manager import ConfigManager
from .constants import ENHANCEMENT_STYLES
from .enhancer import PromptEnhancer

logger = logging.getLogger(__name__)

# Configure CustomTkinter appearance
ctk.set_appearance_mode("System")  # Follows Windows light/dark mode
ctk.set_default_color_theme("blue")


class SettingsWindow:
    """Settings window with tabbed interface."""

    def __init__(
        self,
        config: ConfigManager,
        enhancer: PromptEnhancer,
        on_hotkey_changed=None,
        on_style_changed=None,
        on_save=None,
    ):
        self._config = config
        self._enhancer = enhancer
        self._on_hotkey_changed = on_hotkey_changed
        self._on_style_changed = on_style_changed
        self._on_save = on_save
        self._window = None
        self._is_recording_hotkey = False

    def show(self):
        """Show the settings window. Creates it if not exists."""
        if self._window is not None and self._window.winfo_exists():
            self._window.focus_force()
            self._window.lift()
            return

        self._create_window()

    def _create_window(self):
        """Create the settings window and all its widgets."""
        self._window = ctk.CTkToplevel()
        self._window.title("⚡ PromptEnhancer Settings")
        self._window.geometry("520x480")
        self._window.minsize(480, 440)
        self._window.resizable(True, True)

        # Center on screen
        self._window.update_idletasks()
        x = (self._window.winfo_screenwidth() - 520) // 2
        y = (self._window.winfo_screenheight() - 480) // 2
        self._window.geometry(f"520x480+{x}+{y}")

        # Keep on top briefly so it appears above other windows
        self._window.attributes("-topmost", True)
        self._window.after(500, lambda: self._window.attributes("-topmost", False))

        # ── Main container ───────────────────────────────────────────────
        main_frame = ctk.CTkFrame(self._window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # ── Title ────────────────────────────────────────────────────────
        title_label = ctk.CTkLabel(
            main_frame,
            text="⚡ PromptEnhancer Settings",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(0, 12))

        # ── Tabs ─────────────────────────────────────────────────────────
        self._tabview = ctk.CTkTabview(main_frame, height=320)
        self._tabview.pack(fill="both", expand=True)

        self._tabview.add("🔑 API Key")
        self._tabview.add("✨ Style")
        self._tabview.add("⌨️ Hotkey")
        self._tabview.add("⚙ General")

        self._build_api_tab(self._tabview.tab("🔑 API Key"))
        self._build_style_tab(self._tabview.tab("✨ Style"))
        self._build_hotkey_tab(self._tabview.tab("⌨️ Hotkey"))
        self._build_general_tab(self._tabview.tab("⚙ General"))

        # ── Bottom Buttons ───────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(12, 0))

        self._save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Save Settings",
            command=self._save,
            width=160,
            height=36,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self._save_btn.pack(side="left", padx=(0, 8))

        self._cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self._cancel,
            width=100,
            height=36,
            fg_color="gray40",
            hover_color="gray50",
        )
        self._cancel_btn.pack(side="left")

    # ── API Key Tab ──────────────────────────────────────────────────────

    def _build_api_tab(self, parent):
        """Build the API Key configuration tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        # API Key label
        ctk.CTkLabel(
            frame, text="Groq API Key", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 4))

        # API Key entry
        key_frame = ctk.CTkFrame(frame, fg_color="transparent")
        key_frame.pack(fill="x", pady=(0, 8))

        self._api_key_var = ctk.StringVar(value=self._config.get_api_key())
        self._api_key_entry = ctk.CTkEntry(
            key_frame,
            textvariable=self._api_key_var,
            show="•",
            placeholder_text="Enter your Groq API key...",
            height=36,
        )
        self._api_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self._show_key_btn = ctk.CTkButton(
            key_frame,
            text="👁",
            width=36,
            height=36,
            command=self._toggle_key_visibility,
        )
        self._show_key_btn.pack(side="right")

        # Test button + status
        test_frame = ctk.CTkFrame(frame, fg_color="transparent")
        test_frame.pack(fill="x", pady=(0, 8))

        self._test_btn = ctk.CTkButton(
            test_frame,
            text="🧪 Test API Key",
            command=self._test_api_key,
            width=140,
            height=32,
        )
        self._test_btn.pack(side="left")

        self._test_status = ctk.CTkLabel(
            test_frame, text="", font=ctk.CTkFont(size=12)
        )
        self._test_status.pack(side="left", padx=(10, 0))

        # Info section
        info_frame = ctk.CTkFrame(frame, corner_radius=8)
        info_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            info_frame,
            text="🔗 Get a free API key:",
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=12, pady=(8, 2))

        link_btn = ctk.CTkButton(
            info_frame,
            text="console.groq.com →",
            command=lambda: webbrowser.open("https://console.groq.com"),
            fg_color="transparent",
            text_color=("dodgerblue", "deepskyblue"),
            hover_color=("gray90", "gray25"),
            height=24,
            anchor="w",
        )
        link_btn.pack(anchor="w", padx=12)

        ctk.CTkLabel(
            info_frame,
            text="ℹ Free tier: 30 req/min • 14,400 req/day",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        ).pack(anchor="w", padx=12, pady=(2, 8))

    def _toggle_key_visibility(self):
        """Toggle API key visibility between masked and visible."""
        current = self._api_key_entry.cget("show")
        if current == "•":
            self._api_key_entry.configure(show="")
            self._show_key_btn.configure(text="🔒")
        else:
            self._api_key_entry.configure(show="•")
            self._show_key_btn.configure(text="👁")

    def _test_api_key(self):
        """Test the API key in a background thread."""
        key = self._api_key_var.get().strip()
        if not key:
            self._test_status.configure(text="Enter a key first.", text_color="orange")
            return

        self._test_btn.configure(state="disabled", text="Testing...")
        self._test_status.configure(text="⏳ Testing...", text_color="gray60")

        def do_test():
            success, message = self._enhancer.test_connection(api_key=key)
            # Update UI from the main thread
            if self._window and self._window.winfo_exists():
                self._window.after(0, lambda: self._on_test_result(success, message))

        t = threading.Thread(target=do_test, daemon=True)
        t.start()

    def _on_test_result(self, success: bool, message: str):
        """Handle API test result (called on main thread)."""
        color = ("green", "lime") if success else ("red", "tomato")
        self._test_status.configure(text=message, text_color=color)
        self._test_btn.configure(state="normal", text="🧪 Test API Key")

    # ── Style Tab ────────────────────────────────────────────────────────

    def _build_style_tab(self, parent):
        """Build the Enhancement Style selection tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(
            frame,
            text="Enhancement Style",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        self._style_var = ctk.StringVar(value=self._config.enhancement_style)

        for key, style in ENHANCEMENT_STYLES.items():
            style_frame = ctk.CTkFrame(frame, corner_radius=8)
            style_frame.pack(fill="x", pady=3)

            rb = ctk.CTkRadioButton(
                style_frame,
                text=f"{style['icon']} {style['name']}",
                variable=self._style_var,
                value=key,
                font=ctk.CTkFont(size=13, weight="bold"),
            )
            rb.pack(anchor="w", padx=12, pady=(8, 2))

            ctk.CTkLabel(
                style_frame,
                text=style["description"],
                font=ctk.CTkFont(size=11),
                text_color="gray60",
            ).pack(anchor="w", padx=36, pady=(0, 8))

    # ── Hotkey Tab ───────────────────────────────────────────────────────

    def _build_hotkey_tab(self, parent):
        """Build the Hotkey configuration tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(
            frame,
            text="Keyboard Shortcut",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 8))

        # Current hotkey display
        hotkey_frame = ctk.CTkFrame(frame, corner_radius=8)
        hotkey_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            hotkey_frame,
            text="Current Shortcut:",
            font=ctk.CTkFont(size=12),
        ).pack(anchor="w", padx=12, pady=(8, 4))

        self._hotkey_display = ctk.CTkLabel(
            hotkey_frame,
            text=self._config.hotkey.upper().replace("+", " + "),
            font=ctk.CTkFont(size=18, weight="bold", family="Consolas"),
            text_color=("dodgerblue", "deepskyblue"),
        )
        self._hotkey_display.pack(anchor="w", padx=12, pady=(0, 8))

        # Record new hotkey button
        self._hotkey_var = ctk.StringVar(value=self._config.hotkey)

        self._record_btn = ctk.CTkButton(
            frame,
            text="🎯 Record New Shortcut",
            command=self._start_recording,
            width=200,
            height=36,
        )
        self._record_btn.pack(anchor="w", pady=(0, 8))

        self._hotkey_status = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(size=11), text_color="gray60"
        )
        self._hotkey_status.pack(anchor="w")

        # Reset to default
        ctk.CTkButton(
            frame,
            text="↩ Reset to Default (Ctrl+Shift+E)",
            command=self._reset_hotkey,
            width=240,
            height=30,
            fg_color="gray40",
            hover_color="gray50",
        ).pack(anchor="w", pady=(8, 0))

    def _start_recording(self):
        """Start recording a new hotkey combination."""
        import keyboard as kb

        self._is_recording_hotkey = True
        self._record_btn.configure(
            text="⏺ Press your shortcut...",
            fg_color="orange",
        )
        self._hotkey_status.configure(
            text="Press the key combination you want to use.",
            text_color="orange",
        )

        def on_key_event(event):
            if event.event_type == "down":
                # Build the hotkey string from currently pressed keys
                hotkey = kb.read_hotkey(suppress=False)
                if hotkey and "+" in hotkey:  # Must be a combo
                    self._hotkey_var.set(hotkey)
                    if self._window and self._window.winfo_exists():
                        self._window.after(0, lambda: self._finish_recording(hotkey))
                    kb.unhook(hook)

        hook = kb.hook(on_key_event, suppress=False)

    def _finish_recording(self, hotkey: str):
        """Finish recording the new hotkey."""
        self._is_recording_hotkey = False
        display = hotkey.upper().replace("+", " + ")
        self._hotkey_display.configure(text=display)
        self._record_btn.configure(
            text="🎯 Record New Shortcut",
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
        )
        self._hotkey_status.configure(
            text=f"New shortcut: {display}",
            text_color=("green", "lime"),
        )

    def _reset_hotkey(self):
        """Reset hotkey to default."""
        from .constants import DEFAULT_HOTKEY

        self._hotkey_var.set(DEFAULT_HOTKEY)
        self._hotkey_display.configure(
            text=DEFAULT_HOTKEY.upper().replace("+", " + ")
        )
        self._hotkey_status.configure(
            text="Reset to default.", text_color="gray60"
        )

    # ── General Tab ──────────────────────────────────────────────────────

    def _build_general_tab(self, parent):
        """Build the General settings tab."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=8, pady=8)

        ctk.CTkLabel(
            frame,
            text="General Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 12))

        # Auto-start toggle
        autostart_frame = ctk.CTkFrame(frame, corner_radius=8)
        autostart_frame.pack(fill="x", pady=(0, 8))

        self._autostart_var = ctk.BooleanVar(value=self._config.auto_start)

        autostart_inner = ctk.CTkFrame(autostart_frame, fg_color="transparent")
        autostart_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            autostart_inner,
            text="🚀 Start with Windows",
            font=ctk.CTkFont(size=13),
        ).pack(side="left")

        ctk.CTkSwitch(
            autostart_inner,
            text="",
            variable=self._autostart_var,
            onvalue=True,
            offvalue=False,
        ).pack(side="right")

        # Model selection
        model_frame = ctk.CTkFrame(frame, corner_radius=8)
        model_frame.pack(fill="x", pady=(0, 8))

        model_inner = ctk.CTkFrame(model_frame, fg_color="transparent")
        model_inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(
            model_inner,
            text="🤖 AI Model",
            font=ctk.CTkFont(size=13),
        ).pack(side="left")

        self._model_var = ctk.StringVar(value=self._config.model)
        model_menu = ctk.CTkOptionMenu(
            model_inner,
            variable=self._model_var,
            values=[
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "deepseek-r1-distill-llama-70b",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ],
            width=220,
        )
        model_menu.pack(side="right")

        # App info
        info_frame = ctk.CTkFrame(frame, corner_radius=8)
        info_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            info_frame,
            text="PromptEnhancer v1.0.0",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        ).pack(padx=12, pady=6)

    # ── Save / Cancel ────────────────────────────────────────────────────

    def _save(self):
        """Save all settings and close."""
        # API Key
        new_key = self._api_key_var.get().strip()
        if new_key:
            self._config.set_api_key(new_key)
            self._enhancer.api_key = new_key

        # Style
        new_style = self._style_var.get()
        old_style = self._config.enhancement_style
        self._config.enhancement_style = new_style
        if new_style != old_style and self._on_style_changed:
            self._on_style_changed(new_style)

        # Hotkey
        new_hotkey = self._hotkey_var.get()
        old_hotkey = self._config.hotkey
        self._config.hotkey = new_hotkey
        if new_hotkey != old_hotkey and self._on_hotkey_changed:
            self._on_hotkey_changed(new_hotkey)

        # Auto-start
        new_autostart = self._autostart_var.get()
        self._config.auto_start = new_autostart
        self._config.set_auto_start_registry(new_autostart)

        # Model
        new_model = self._model_var.get()
        self._config.model = new_model
        self._enhancer.model = new_model

        # First run flag
        self._config.first_run = False

        # Persist
        self._config.save()

        logger.info("Settings saved.")
        self._window.destroy()
        self._window = None

        if self._on_save:
            self._on_save()

    def _cancel(self):
        """Close without saving."""
        self._window.destroy()
        self._window = None

    @property
    def is_open(self) -> bool:
        """Check if the settings window is currently open."""
        return self._window is not None and self._window.winfo_exists()


class HistoryWindow:
    """Simple history viewer window using CustomTkinter."""

    def __init__(self, history_data: list[dict], on_clear=None):
        self._history = history_data
        self._on_clear = on_clear
        self._window = None

    def show(self):
        """Show the history window."""
        if self._window is not None and self._window.winfo_exists():
            self._window.focus_force()
            self._window.lift()
            return

        self._create_window()

    def _create_window(self):
        """Create the history viewer window."""
        self._window = ctk.CTkToplevel()
        self._window.title("📋 Enhancement History")
        self._window.geometry("600x500")
        self._window.minsize(500, 400)

        # Center
        self._window.update_idletasks()
        x = (self._window.winfo_screenwidth() - 600) // 2
        y = (self._window.winfo_screenheight() - 500) // 2
        self._window.geometry(f"600x500+{x}+{y}")

        self._window.attributes("-topmost", True)
        self._window.after(500, lambda: self._window.attributes("-topmost", False))

        # Main container
        main = ctk.CTkFrame(self._window, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=16, pady=16)

        # Title row
        title_row = ctk.CTkFrame(main, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            title_row,
            text=f"📋 Enhancement History ({len(self._history)} entries)",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(side="left")

        if self._history:
            ctk.CTkButton(
                title_row,
                text="🗑 Clear All",
                command=self._clear_history,
                width=100,
                height=30,
                fg_color="red",
                hover_color="darkred",
            ).pack(side="right")

        # Scrollable list
        scroll_frame = ctk.CTkScrollableFrame(main, corner_radius=8)
        scroll_frame.pack(fill="both", expand=True)

        if not self._history:
            ctk.CTkLabel(
                scroll_frame,
                text="No history yet.\nEnhance some prompts to see them here!",
                font=ctk.CTkFont(size=13),
                text_color="gray60",
            ).pack(pady=40)
        else:
            for i, entry in enumerate(self._history):
                self._add_history_card(scroll_frame, entry, i)

    def _add_history_card(self, parent, entry: dict, index: int):
        """Add a single history entry card."""
        card = ctk.CTkFrame(parent, corner_radius=8)
        card.pack(fill="x", pady=4, padx=4)

        # Header: timestamp + style
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(8, 4))

        timestamp = entry.get("timestamp", "Unknown")[:19].replace("T", " ")
        style_name = ENHANCEMENT_STYLES.get(
            entry.get("style", "standard"), {}
        ).get("name", "Standard")

        ctk.CTkLabel(
            header,
            text=f"🕐 {timestamp}",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=f"Style: {style_name}",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
        ).pack(side="right")

        # Original text preview
        original = entry.get("original", "")[:100]
        if len(entry.get("original", "")) > 100:
            original += "..."

        ctk.CTkLabel(
            card,
            text=f"📝 Original: {original}",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            wraplength=540,
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 2))

        # Enhanced text preview
        enhanced = entry.get("enhanced", "")[:150]
        if len(entry.get("enhanced", "")) > 150:
            enhanced += "..."

        ctk.CTkLabel(
            card,
            text=f"✨ Enhanced: {enhanced}",
            font=ctk.CTkFont(size=11),
            wraplength=540,
            justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 4))

        # Copy button
        def copy_enhanced(text=entry.get("enhanced", "")):
            import pyperclip
            try:
                pyperclip.copy(text)
            except Exception:
                # Fallback: use win32clipboard
                try:
                    import win32clipboard
                    import win32con
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
                    win32clipboard.CloseClipboard()
                except Exception:
                    pass

        ctk.CTkButton(
            card,
            text="📋 Copy Enhanced",
            command=copy_enhanced,
            width=130,
            height=26,
            font=ctk.CTkFont(size=11),
        ).pack(anchor="e", padx=10, pady=(0, 8))

    def _clear_history(self):
        """Clear all history."""
        if self._on_clear:
            self._on_clear()
        self._window.destroy()
        self._window = None
