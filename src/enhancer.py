"""
PromptEnhancer — Groq API integration for prompt enhancement.

Sends selected text to the Groq API with a style-specific system prompt
and returns the enhanced prompt text.
"""

import logging

import requests

from .constants import (
    API_TIMEOUT,
    ENHANCEMENT_STYLES,
    GROQ_API_ENDPOINT,
)

logger = logging.getLogger(__name__)


# ── Custom Exceptions ────────────────────────────────────────────────────────

class EnhancerError(Exception):
    """Base exception for enhancer errors."""
    pass


class InvalidAPIKeyError(EnhancerError):
    """API key is invalid or expired."""
    pass


class RateLimitError(EnhancerError):
    """API rate limit has been reached."""
    pass


class NetworkError(EnhancerError):
    """Network connectivity issue."""
    pass


class TimeoutError(EnhancerError):
    """API request timed out."""
    pass


class APIError(EnhancerError):
    """Generic API error."""
    pass


# ── Prompt Enhancer ──────────────────────────────────────────────────────────

class PromptEnhancer:
    """Enhances prompts using the Groq LLM API."""

    def __init__(self, api_key: str = "", model: str = ""):
        self._api_key = api_key
        self._model = model

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str):
        self._api_key = value

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str):
        self._model = value

    def enhance(self, text: str, style: str = "standard") -> str:
        """
        Enhance a text prompt using the configured LLM API.

        Args:
            text: The raw prompt text to enhance.
            style: Enhancement style key (standard, detailed, concise, creative).

        Returns:
            The enhanced prompt text.

        Raises:
            InvalidAPIKeyError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            NetworkError: If there's no internet connection.
            TimeoutError: If the request times out.
            APIError: For any other API error.
        """
        if not self._api_key:
            raise InvalidAPIKeyError("No API key configured.")

        # Get the system prompt for the selected style
        style_config = ENHANCEMENT_STYLES.get(style, ENHANCEMENT_STYLES["standard"])
        system_prompt = style_config["system_prompt"]

        # Build the request
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.7,
            "max_tokens": 2048,
        }

        # Make the API call
        try:
            response = requests.post(
                GROQ_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=API_TIMEOUT,
            )
        except requests.exceptions.ConnectionError:
            raise NetworkError("No internet connection.")
        except requests.exceptions.Timeout:
            raise TimeoutError("Request timed out.")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

        # Handle response
        if response.status_code == 200:
            try:
                data = response.json()
                enhanced = data["choices"][0]["message"]["content"]
                return enhanced.strip()
            except (KeyError, IndexError, ValueError) as e:
                raise APIError(f"Unexpected API response format: {e}")

        elif response.status_code == 401:
            raise InvalidAPIKeyError("Invalid API key.")

        elif response.status_code == 429:
            raise RateLimitError("Rate limit reached. Wait 1 minute.")

        elif response.status_code == 408:
            raise TimeoutError("Request timed out.")

        else:
            error_msg = ""
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "")
            except Exception:
                error_msg = response.text[:200]
            raise APIError(
                f"API error (HTTP {response.status_code}): {error_msg}"
            )

    def test_connection(self, api_key: str = None) -> tuple[bool, str]:
        """
        Test the API connection with a simple request.

        Args:
            api_key: Optional API key to test (uses stored key if not provided).

        Returns:
            Tuple of (success: bool, message: str).
        """
        test_key = api_key or self._api_key
        if not test_key:
            return False, "No API key provided."

        headers = {
            "Authorization": f"Bearer {test_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "messages": [
                {"role": "user", "content": "Say 'OK' and nothing else."},
            ],
            "temperature": 0,
            "max_tokens": 5,
        }

        try:
            response = requests.post(
                GROQ_API_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                return True, "Connection successful! ✅"
            elif response.status_code == 401:
                return False, "Invalid API key. ❌"
            elif response.status_code == 429:
                return False, "Rate limit reached. Try again later. ⚠"
            else:
                return False, f"API error (HTTP {response.status_code}). ❌"

        except requests.exceptions.ConnectionError:
            return False, "No internet connection. ❌"
        except requests.exceptions.Timeout:
            return False, "Connection timed out. ❌"
        except Exception as e:
            return False, f"Error: {str(e)} ❌"
