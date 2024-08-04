# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Process Image Module"""

from typing import Any, Dict, Union

from server.common import gemini


class ImageProcessor:
    """Process an image."""
    def __init__(self, image_contents):
        """Init image processor.

        Args:
            gcs_uri: GCS path of image.
        """
        # Image as part.
        self.image_contents = image_contents

        self.model = gemini.GeminiModelManager()

    async def classify_image(self, prompt: str) -> str:
        """Classify an image.

        Args:
            prompt: Classification prompt.
        """
        result = await self.model.generate_response(
            contents=[self.image_contents, prompt],
        )
        return result

    async def extract_image_contents(
            self,
            prompt: str,
            response_mime_type: str = "application/json"
        ) -> Union[str, Dict[str, Any]]:
        """Extract image contents.

        Args:
            prompt: Extraction prompt.
            response_mime_type: Mime type of extracted contents.
        """
        result = await self.model.generate_response(
            contents=[self.image_contents, prompt],
            response_mime_type=response_mime_type
        )
        return result
