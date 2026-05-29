from typing import Any

import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class NanoBananaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the Gemini API key by listing available models.
        """
        api_key = credentials.get("gemini_api_key", "")
        if not api_key:
            raise ToolProviderCredentialValidationError("Gemini API Key is required.")

        try:
            response = requests.get(
                url=GEMINI_MODELS_URL,
                headers={"x-goog-api-key": api_key},
                timeout=(5, 30),
            )
            if response.status_code in (400, 401, 403):
                raise ToolProviderCredentialValidationError("Invalid Gemini API Key.")
            if not response.ok:
                raise ToolProviderCredentialValidationError(
                    f"Failed to validate API Key: HTTP {response.status_code}"
                )
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to validate credentials: {str(e)}"
            )
