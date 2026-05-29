import base64
from typing import Any

import requests

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Model identifiers
MODEL_NANO_BANANA = "gemini-2.5-flash-image"
MODEL_NANO_BANANA_2 = "gemini-3.1-flash-image-preview"
MODEL_NANO_BANANA_PRO = "gemini-3.1-pro-image"

MODEL_IDS = {
    "nano_banana": MODEL_NANO_BANANA,
    "nano_banana_2": MODEL_NANO_BANANA_2,
    "nano_banana_pro": MODEL_NANO_BANANA_PRO,
}

MAX_INPUT_IMAGES = {
    "nano_banana": 3,
    "nano_banana_2": 14,
    "nano_banana_pro": 14,
}

SUPPORTED_ASPECT_RATIOS = {
    "nano_banana": {
        "1:1",
        "2:3",
        "3:2",
        "3:4",
        "4:3",
        "4:5",
        "5:4",
        "9:16",
        "16:9",
        "21:9",
    },
    "nano_banana_2": {
        "1:1",
        "1:4",
        "4:1",
        "1:8",
        "8:1",
        "2:3",
        "3:2",
        "3:4",
        "4:3",
        "4:5",
        "5:4",
        "9:16",
        "16:9",
        "21:9",
    },
    "nano_banana_pro": {
        "1:1",
        "2:3",
        "3:2",
        "3:4",
        "4:3",
        "4:5",
        "5:4",
        "9:16",
        "16:9",
        "21:9",
    },
}

SUPPORTED_IMAGE_SIZES = {
    "nano_banana": set(),
    "nano_banana_2": {"512", "1K", "2K", "4K"},
    "nano_banana_pro": {"1K", "2K", "4K"},
}

GOOGLE_SEARCH_MODELS = {"nano_banana_2", "nano_banana_pro"}


class NanoBananaBase:
    """
    Base class for Nano Banana (Gemini Image Generation) tools.
    Uses Google's official Gemini REST API (generativelanguage.googleapis.com).
    """

    def _get_model_name(self, model: str) -> str:
        """Get the Gemini model identifier string."""
        if model not in MODEL_IDS:
            raise ValueError(f"Unsupported model: {model}")
        return MODEL_IDS[model]

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

    def _validate_image_options(
        self,
        model: str,
        aspect_ratio: str = "",
        image_size: str = "",
        use_google_search: bool = False,
    ) -> None:
        """Validate model-specific image generation options before calling Gemini."""
        if model not in MODEL_IDS:
            raise ValueError(f"Unsupported model: {model}")

        if aspect_ratio and aspect_ratio not in SUPPORTED_ASPECT_RATIOS[model]:
            supported = ", ".join(sorted(SUPPORTED_ASPECT_RATIOS[model]))
            raise ValueError(
                f"Aspect ratio {aspect_ratio} is not supported by {MODEL_IDS[model]}. "
                f"Supported values: {supported}"
            )

        if image_size and image_size not in SUPPORTED_IMAGE_SIZES[model]:
            supported_sizes = SUPPORTED_IMAGE_SIZES[model]
            if supported_sizes:
                supported = ", ".join(sorted(supported_sizes))
                raise ValueError(
                    f"Image size {image_size} is not supported by {MODEL_IDS[model]}. "
                    f"Supported values: {supported}"
                )
            raise ValueError(f"Image size is not supported by {MODEL_IDS[model]}")

        if use_google_search and model not in GOOGLE_SEARCH_MODELS:
            raise ValueError(
                f"Google Search grounding is not supported by {MODEL_IDS[model]}"
            )

    def _validate_image_count(self, model: str, image_count: int) -> None:
        """Validate the number of reference images for edit workflows."""
        if model not in MODEL_IDS:
            raise ValueError(f"Unsupported model: {model}")

        max_images = MAX_INPUT_IMAGES[model]
        if image_count > max_images:
            raise ValueError(
                f"{MODEL_IDS[model]} supports at most {max_images} input images; "
                f"received {image_count}."
            )

    def _as_bool(self, value: Any) -> bool:
        """Coerce Dify form values to bool."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "1", "yes", "on"}
        return bool(value)

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
            model: "nano_banana", "nano_banana_2", or "nano_banana_pro"
            aspect_ratio: e.g. "1:1", "16:9"
            image_size: e.g. "512", "1K", "2K", "4K"
            response_modalities: e.g. ["TEXT", "IMAGE"] or ["IMAGE"]
        """
        config: dict[str, Any] = {}

        if response_modalities:
            config["responseModalities"] = response_modalities

        image_config: dict[str, Any] = {}
        if aspect_ratio:
            image_config["aspectRatio"] = aspect_ratio
        if image_size:
            image_config["imageSize"] = image_size
        if image_config:
            config["imageConfig"] = image_config

        return config

    def _add_google_search_tool(
        self,
        body: dict[str, Any],
        model: str,
        use_google_search: bool = False,
    ) -> None:
        """Enable Google Search grounding for Gemini 3 image models."""
        if use_google_search:
            self._validate_image_options(model, use_google_search=True)
            body["tools"] = [{"google_search": {}}]

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
            timeout=(10, 290),
        )

        if not response.ok:
            error_detail = self._format_error_response(response)
            raise Exception(
                f"Gemini API error: HTTP {response.status_code} - {error_detail}"
            )

        return response.json()

    def _format_error_response(self, response: requests.Response) -> str:
        """Extract a compact Gemini error message from an HTTP response."""
        try:
            error = response.json().get("error", {})
            message = error.get("message")
            status = error.get("status")
            if message and status:
                return f"{status}: {message}"
            if message:
                return message
        except ValueError:
            pass
        return response.text[:500]

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

        raise Exception(
            "No image data found in Gemini API response. "
            f"{self._format_generation_failure(response_json)}"
        )

    def _format_generation_failure(self, response_json: dict[str, Any]) -> str:
        """Summarize finish and safety metadata when Gemini returns no image."""
        candidates = response_json.get("candidates", [])
        candidate = candidates[0] if candidates else {}
        details = []

        finish_reason = candidate.get("finishReason")
        if finish_reason:
            details.append(f"finishReason={finish_reason}")

        prompt_feedback = response_json.get("promptFeedback")
        if prompt_feedback:
            details.append(f"promptFeedback={prompt_feedback}")

        safety_ratings = candidate.get("safetyRatings")
        if safety_ratings:
            details.append(f"safetyRatings={safety_ratings}")

        text = self._extract_text_from_response(response_json)
        if text:
            details.append(f"text={text[:300]}")

        return "; ".join(details) if details else "No diagnostic metadata returned."

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
