import base64
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import NanoBananaBase


class EditImageTool(Tool, NanoBananaBase):
    """
    Edit or transform existing images using Google Gemini's
    native image generation (Nano Banana) with natural language instructions.
    Uses the official Gemini generateContent REST API.
    Accepts file inputs (Array[File]) from Dify workflow/agent.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        # Extract parameters
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            raise ValueError("Edit prompt is required")

        # Get file inputs - Dify passes files as a list of File objects
        files = tool_parameters.get("images", [])
        if not files:
            raise ValueError("At least one image is required")

        model = tool_parameters.get("model", "nano_banana")
        aspect_ratio = tool_parameters.get("aspect_ratio", "")
        image_size = tool_parameters.get("image_size", "")
        credentials = self.runtime.credentials

        # Convert Dify File objects to base64 inline_data for Gemini API
        image_data_list = []
        for file in files:
            # Dify File object has .blob (bytes) and .mime_type properties
            file_bytes = file.blob
            mime_type = file.mime_type or "image/png"
            encoded = base64.b64encode(file_bytes).decode("utf-8")
            image_data_list.append({
                "mime_type": mime_type,
                "data": encoded,
            })

        # Build request body with text prompt + inline image data
        body = self._build_text_and_images_content(prompt, image_data_list)

        # Build generationConfig
        gen_config = self._build_generation_config(
            model=model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            response_modalities=["TEXT", "IMAGE"],
        )
        if gen_config:
            body["generationConfig"] = gen_config

        # Call Gemini API (synchronous — returns image immediately)
        response_json = self._call_gemini_api(credentials, model, body)

        # Extract and return the image
        image_data = self._extract_image_from_response(response_json)
        mime_type = self._get_image_mime_type(response_json)

        yield self.create_blob_message(
            blob=image_data, meta={"mime_type": mime_type}
        )

        # Also yield any text description
        text = self._extract_text_from_response(response_json)
        if text:
            yield self.create_text_message(text)
