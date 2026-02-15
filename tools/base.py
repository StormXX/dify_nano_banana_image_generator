import base64
from typing import Any

import requests

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Model identifiers
MODEL_FLASH = "gemini-2.5-flash-image"  # Nano Banana (fast, efficient)
MODEL_PRO = "gemini-3-pro-image-preview"  # Nano Banana Pro (high quality, 4K)


class NanoBananaBase:
    """
    Base class for Nano Banana (Gemini Image Generation) tools.
    Uses Google's official Gemini REST API (generativelanguage.googleapis.com).
    """

    def _get_model_name(self, model: str) -> str:
        """Get the Gemini model identifier string."""
        if model == "nano_banana_pro":
            return MODEL_PRO
        return MODEL_FLASH

    def _get_generate_url(self, model_name: str) -> str:
        """Get the generateContent API endpoint URL for the given model."""
        return f"{GEMINI_API_BASE}/{model_name}:generateContent"

    def _build_request_headers(self, credentials: dict[str, Any]) -> dict[str, str]:
        """Build request headers with Gemini API key."""
        api_key = credentials.get("gemini_api_key", "")
        return {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        }

    def _build_generation_config(
        self,
        model: str,
        aspect_ratio: str = "",
        image_size: str = "",
        response_modalities: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Build the generationConfig for the API request.

        Args:
            model: "nano_banana" or "nano_banana_pro"
            aspect_ratio: e.g. "1:1", "16:9"
            image_size: e.g. "1K", "2K", "4K" (Pro model only)
            response_modalities: e.g. ["TEXT", "IMAGE"] or ["IMAGE"]
        """
        config: dict[str, Any] = {}

        if response_modalities:
            config["responseModalities"] = response_modalities

        image_config: dict[str, Any] = {}
        if aspect_ratio:
            image_config["aspectRatio"] = aspect_ratio
        if image_size and model == "nano_banana_pro":
            image_config["imageSize"] = image_size
        if image_config:
            config["imageConfig"] = image_config

        return config

    def _build_text_content(self, prompt: str) -> dict[str, Any]:
        """Build a contents entry with just a text prompt."""
        return {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

    def _build_text_and_images_content(
        self, prompt: str, image_data_list: list[dict[str, str]]
    ) -> dict[str, Any]:
        """
        Build a contents entry with text prompt and inline image data.

        Args:
            prompt: Text prompt
            image_data_list: List of dicts with "mime_type" and "data" (base64)
        """
        parts: list[dict[str, Any]] = [{"text": prompt}]
        for img in image_data_list:
            parts.append({
                "inline_data": {
                    "mime_type": img["mime_type"],
                    "data": img["data"],
                }
            })
        return {
            "contents": [{
                "parts": parts
            }]
        }

    def _call_gemini_api(
        self,
        credentials: dict[str, Any],
        model: str,
        request_body: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Call the Gemini generateContent API and return the response JSON.
        This is a synchronous call — the image is returned immediately.
        """
        model_name = self._get_model_name(model)
        url = self._get_generate_url(model_name)
        headers = self._build_request_headers(credentials)

        response = requests.post(
            url=url,
            headers=headers,
            json=request_body,
            timeout=(10, 120),
        )

        if not response.ok:
            error_detail = response.text[:500]
            raise Exception(
                f"Gemini API error: HTTP {response.status_code} - {error_detail}"
            )

        return response.json()

    def _extract_image_from_response(self, response_json: dict[str, Any]) -> bytes:
        """
        Extract the first image from a Gemini API response.
        Images are returned as base64-encoded inline_data in response parts.
        Returns raw image bytes.
        """
        candidates = response_json.get("candidates", [])
        if not candidates:
            raise Exception("No candidates in Gemini API response")

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline_data = part.get("inlineData")
            if inline_data and inline_data.get("data"):
                return base64.b64decode(inline_data["data"])

        raise Exception("No image data found in Gemini API response")

    def _extract_text_from_response(self, response_json: dict[str, Any]) -> str:
        """Extract text from a Gemini API response, if any."""
        candidates = response_json.get("candidates", [])
        if not candidates:
            return ""

        parts = candidates[0].get("content", {}).get("parts", [])
        texts = []
        for part in parts:
            if "text" in part:
                texts.append(part["text"])
        return "\n".join(texts)

    def _get_image_mime_type(self, response_json: dict[str, Any]) -> str:
        """Extract the MIME type of the returned image."""
        candidates = response_json.get("candidates", [])
        if not candidates:
            return "image/png"

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline_data = part.get("inlineData")
            if inline_data:
                return inline_data.get("mimeType", "image/png")
        return "image/png"

    def _download_image_as_base64(self, image_url: str) -> dict[str, str]:
        """
        Download an image from URL and return it as base64 data
        suitable for inline_data in a Gemini API request.
        """
        response = requests.get(url=image_url, timeout=(10, 60))
        if not response.ok:
            raise Exception(
                f"Failed to download image from {image_url}: HTTP {response.status_code}"
            )

        # Determine mime type from response headers
        content_type = response.headers.get("Content-Type", "image/png")
        if ";" in content_type:
            content_type = content_type.split(";")[0].strip()

        encoded = base64.b64encode(response.content).decode("utf-8")
        return {
            "mime_type": content_type,
            "data": encoded,
        }
