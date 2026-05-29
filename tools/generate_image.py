from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import NanoBananaBase


class GenerateImageTool(Tool, NanoBananaBase):
    """
    Generate images from text prompts using Google Gemini's
    native image generation models.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            raise ValueError("Prompt is required")

        model = tool_parameters.get("model", "nano_banana_2")
        aspect_ratio = tool_parameters.get("aspect_ratio", "")
        image_size = tool_parameters.get("image_size", "")
        use_google_search = self._as_bool(
            tool_parameters.get("use_google_search", False)
        )
        credentials = self.runtime.credentials

        self._validate_image_options(
            model=model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            use_google_search=use_google_search,
        )

        body = self._build_text_content(prompt)

        gen_config = self._build_generation_config(
            model=model,
            aspect_ratio=aspect_ratio,
            image_size=image_size,
            response_modalities=["TEXT", "IMAGE"],
        )
        if gen_config:
            body["generationConfig"] = gen_config
        self._add_google_search_tool(body, model, use_google_search)

        response_json = self._call_gemini_api(credentials, model, body)

        image_data = self._extract_image_from_response(response_json)
        mime_type = self._get_image_mime_type(response_json)

        yield self.create_blob_message(
            blob=image_data, meta={"mime_type": mime_type}
        )

        text = self._extract_text_from_response(response_json)
        if text:
            yield self.create_text_message(text)
