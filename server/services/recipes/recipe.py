# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Recipe Module."""

from typing import Any, Dict, List

from server.common import prompts
from server.services.diy import diy_recommendation_data


class Recipe:
    """Module for generating data for single recipe."""
    def __init__(
        self,
        recipe: str,
        product_list: List[str]
    ):
        """Init Recipe module.

        Generates additional metadata for each recipe.
        This includes nutritional information, ingredients, and instrucitons.
        Grounds the ingredients generated based on the grocery list generated.
        The product list is used to ground the recipe ingredients generated
        into what will be mapped to the product catalog.

        Args:
            recipe: Recipe name
            product_list: Product list generated

        """
        self.recipe = recipe
        self.product_list = product_list

    async def get_recipe_data(self) -> Dict[str, Any]:
        """Get metadata for recipe."""
        prompt = prompts.recipe_data_prompt.format(
            recipe=self.recipe,
            product_list=self.product_list
        )
        diy_rec_data_generator = diy_recommendation_data.DIYRecommendation(
            diy_idea=self.recipe,
            prompt=prompt
        )
        recipe_data = await diy_rec_data_generator.generate_metadata()
        return recipe_data
