# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Gemini Model Functions."""

import json
from typing import Any, Dict, Optional, Union

from vertexai.generative_models import (
    HarmCategory,
    HarmBlockThreshold,
    GenerationConfig,
    GenerationResponse,
    GenerativeModel,
)


DEFAULT_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,  # pylint: disable=line-too-long
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,  # pylint: disable=line-too-long
    HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


class GeminiModelManager:
    """A llm model manager class."""
    def __init__(
        self,
        model_name: str = "gemini-1.5-flash-001",
        system_prompt: Optional[str] = None,
        safety_settings: Optional[Dict[str, Any]] = None,
    ):
        """Initialize a Gemini model instance.

        Args:
            model_name (str, optional): Gemini model name.
            system_prompt (str, optional): A system prompt to
                guide the model's behavior.
            safety_settings (Dict[str, Any], optional): Safety settings
                to control content filtering.
        """
        # Safety settings for model.
        safety_settings = safety_settings or DEFAULT_SAFETY_SETTINGS

        # Add system instruction if not none.
        system_instruction = [system_prompt] if system_prompt else None

        self.model = GenerativeModel(
            model_name=model_name,
            safety_settings=safety_settings,
            system_instruction=system_instruction,
        )

    async def generate_response(
        self,
        contents,
        temperature: Optional[float] = 0.2,
        max_output_tokens:  Optional[int] = 8192,
        top_p: Optional[float] = 0.95,
        response_mime_type: Optional[str] = "text/plain"
    ):
        """Generate LLM response."""
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            response_mime_type=response_mime_type
        )
        response = await self.model.generate_content_async(
            contents=contents,
            generation_config=generation_config
        )

        # If response should be json.
        is_json = response_mime_type != "text/plain"

        # Parse LLM result.
        result = self.parse_gemini_text_response(
            response=response,
            is_json=is_json
        )

        return result

    def parse_gemini_text_response(
        self,
        response: GenerationResponse,
        is_json: bool = False
    ) -> Union[str, Dict]:
        """Extracts text content from Gemini response.

        Args:
            response: Gemini API response object.

        Returns:
            The generated response.
        """
        try:
            part = response.candidates[0].content.parts[0]
            text = part.text.strip()
            if is_json:
                return json.loads(text)
        except Exception:
            text = None
        return text
