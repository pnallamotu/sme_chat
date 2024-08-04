# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""SME Images Module"""

from server.common import prompts
from server.services.image import process_image


class SMEImages:
    """Process an image for SME."""
    def __init__(
            self,
            image_contents
    ):
        self.image_processor = process_image.ImageProcessor(
            image_contents=image_contents)

    async def process_image(self):
        """Process image.

        Classify, extract, and construct query
        based on image contents to an intent for SME.
        """
        # TODO (pnallamotu): Handle case if query is none
        # in API route.
        query = None

        # First classify image.
        image_type = await self.classify_image_type()
        if image_type == "grocery_list":
            # Prompt to extract image grocery list.
            prompt = prompts.image_grocery_list_prompt
            grocery_list = await self.image_processor.extract_image_contents(
                prompt)

            # Convert extracted contents to query.
            # Static query to fit to product recommendations intent.
            query = f"I want recommendations for: {', '.join(grocery_list)}"
        elif image_type == "meal":
            # Prompt to extract image recipe name.
            prompt = prompts.image_recipe_prompt
            recipe_name = await self.image_processor.extract_image_contents(
                prompt)

            # Convert extracted contents to query.
            # Static query to fit to recipe recommendations intent.
            query = f"I want these recipes:  {', '.join(recipe_name)}"

        return query

    async def classify_image_type(self):
        """Classify whether image is recipe or grocery list."""
        prompt = prompts.image_classification_prompt
        return await self.image_processor.classify_image(prompt)
