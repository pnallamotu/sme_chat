# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Save recipes Module."""

import os
from typing import Any, Dict, Optional

from server.common import utils
from server.functions import datastore
from server.services.products import product_search


class SavedRecipes:
    """Saved Recipes."""
    def __init__(
        self,
        project_id: Optional[str] = None,
        recipes_datastore_id: Optional[str] = None,
    ):
        """Init saved recipes datastore manager.

        Args:
            project_id: Project of datastore recipes DB.
            recipes_datastore_id: Recipes datastore DB id.
        """
        self.project_id = project_id or os.getenv("project_id")
        self.recipes_datastore_id = recipes_datastore_id or os.getenv(
            "recipes_datastore_id")

        self.datastore_manager = datastore.DataStoreManager(
            project_id=self.project_id, datastore_id=self.recipes_datastore_id)

    def get_saved_recipes(self):
        """Get saved recipes."""
        return self.datastore_manager.get_saved_elements(
            kind="Recipe"
        )

    async def add_saved_recipe(self, recipe: Dict[str, Any]):
        """Save a recipe."""
        # For a saved recipe, get it's associated grocery list
        # from it's ingredients.
        ingredients = recipe.get("ingredients")

        recipe_products = await utils.make_parallel_calls(
            items=ingredients, async_processing_func=product_search.get_individual_product_type)

        # Update recipe with grocery list.
        recipe.update({
            "grocery_list": recipe_products
        })
        
        recipe_id = recipe.get("id")
        self.datastore_manager.save_element(
            id=recipe_id,
            kind="Recipe",
            elem_key="recipe",
            element=recipe
        )

    def unsave_recipe(self, recipe_id: int):
        """Unsave a recipe."""
        self.datastore_manager.delete_element(
            id=recipe_id,
            kind="Recipe"
        )
