"""
PromptEnhancer — Configuration management with encrypted API key storage.

Stores settings in %APPDATA%/PromptEnhancer/config.json.
API key is encrypted at rest using Fernet symmetric encryption.
"""

import json
import logging
import os

from cryptography.fernet import Fernet, InvalidToken

from .constants import (
    APPDATA_DIR,
    CONFIG_FILE,
    DEFAULT_CONFIG,
    SECRET_KEY_FILE,
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration with encrypted API key storage."""

    def __init__(self):
        self._config = dict(DEFAULT_CONFIG)
        self._fernet = None
        self._ensure_appdata_dir()
        self._init_encryption()
        self.load()

    # ── Directory Setup ──────────────────────────────────────────────────

    def _ensure_appdata_dir(self):
        """Create the AppData directory if it doesn't exist."""
        os.makedirs(APPDATA_DIR, exist_ok=True)

    # ── Encryption ───────────────────────────────────────────────────────

    def _init_encryption(self):
        """Initialize Fernet encryption. Generate key on first run."""
        if not os.path.exists(SECRET_KEY_FILE):
            key = Fernet.generate_key()
            with open(SECRET_KEY_FILE, "wb") as f:
                f.write(key)
            logger.info("Generated new encryption key.")
        
        with open(SECRET_KEY_FILE, "rb") as f:
            key = f.read()
        
        self._fernet = Fernet(key)

    def _encrypt(self, plaintext: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext."""
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def _decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext string."""
        if not ciphertext:
            return ""
        try:
            return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except (InvalidToken, Exception) as e:
            logger.error(f"Failed to decrypt API key: {e}")
            return ""

    # ── Config Load / Save ───────────────────────────────────────────────

    def load(self):
        """Load configuration from disk. Uses defaults if file doesn't exist."""
        if not os.path.exists(CONFIG_FILE):
            logger.info("No config file found. Using defaults.")
            self._config = dict(DEFAULT_CONFIG)
            return

        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge with defaults (so new keys are always present)
            self._config = {**DEFAULT_CONFIG, **saved}
            # Migrate deprecated model
            if self._config.get("model") == "llama-3.1-70b-versatile":
                self._config["model"] = "llama-3.3-70b-versatile"
                self.save()
            logger.info("Configuration loaded.")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load config: {e}. Using defaults.")
            self._config = dict(DEFAULT_CONFIG)

    def save(self):
        """Persist current configuration to disk."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration saved.")
        except IOError as e:
            logger.error(f"Failed to save config: {e}")

    # ── API Key ──────────────────────────────────────────────────────────

    def get_api_key(self) -> str:
        """Decrypt and return the stored API key."""
        return self._decrypt(self._config.get("api_key_encrypted", ""))

    def set_api_key(self, api_key: str):
        """Encrypt and store the API key."""
        self._config["api_key_encrypted"] = self._encrypt(api_key)

    def has_api_key(self) -> bool:
        """Check if an API key is configured."""
        return bool(self.get_api_key())

    # ── Generic Getters / Setters ────────────────────────────────────────

    @property
    def enhancement_style(self) -> str:
        return self._config.get("enhancement_style", "standard")

    @enhancement_style.setter
    def enhancement_style(self, value: str):
        self._config["enhancement_style"] = value

    @property
    def hotkey(self) -> str:
        return self._config.get("hotkey", "ctrl+shift+e")

    @hotkey.setter
    def hotkey(self, value: str):
        self._config["hotkey"] = value

    @property
    def auto_start(self) -> bool:
        return self._config.get("auto_start", False)

    @auto_start.setter
    def auto_start(self, value: bool):
        self._config["auto_start"] = value

    @property
    def model(self) -> str:
        return self._config.get("model", "llama-3.3-70b-versatile")

    @model.setter
    def model(self, value: str):
        self._config["model"] = value

    @property
    def first_run(self) -> bool:
        return self._config.get("first_run", True)

    @first_run.setter
    def first_run(self, value: bool):
        self._config["first_run"] = value

    # ── Auto-Start (Windows Registry) ────────────────────────────────────

    def set_auto_start_registry(self, enable: bool):
        """Add or remove the app from Windows startup via the registry."""
        import sys

        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
            )

            if enable:
                # Use the frozen EXE path or the script path
                if getattr(sys, "frozen", False):
                    exe_path = sys.executable
                else:
                    exe_path = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}"'
                winreg.SetValueEx(key, "PromptEnhancer", 0, winreg.REG_SZ, exe_path)
                logger.info("Auto-start enabled in registry.")
            else:
                try:
                    winreg.DeleteValue(key, "PromptEnhancer")
                    logger.info("Auto-start disabled in registry.")
                except FileNotFoundError:
                    pass  # Key doesn't exist, nothing to remove

            winreg.CloseKey(key)
        except Exception as e:
            logger.error(f"Failed to set auto-start registry: {e}")
