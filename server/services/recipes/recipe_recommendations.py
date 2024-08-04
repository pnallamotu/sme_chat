# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Recipe Recommendations Module."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Dict, Tuple

import asyncio

from server.common import prompts
from server.services.diy import diy_recommendations
from server.services.diy import diy_recommendation_product_list
from server.services.recipes import recipe


class RecipeRecommendations:
    """Generate Recipes."""
    def __init__(
        self,
        query: str = None
    ):
        """Init Recipe Recommendation agent.

        Args:
            query: User query to generate recipes/meal plans for.
        """
        self.query = query

    async def get_recommendations(self):
        """Get recipe recommendations.

        Returns:
            Dictionary of recipes and prodcuts (grocery list).
                - recipes is a list of each recipe with metadata.
                - products is the grocery list to prepare the recipes.
        """
        # Get recommended recipes & grocery list.
        recipe_names, product_list =  await self.get_recipe_recommendations()
        recipes, products = await self.run_in_parallel(recipe_names, product_list)
        return recipes, products

    async def run_in_parallel(self, recipe_names, product_list):
        """Run Recipe & Product in parallel."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            loop = asyncio.get_running_loop()

            def get_recipes_data_sync():
                return asyncio.run_coroutine_threadsafe(
                    self.get_recipes_data(recipe_names=recipe_names, product_list=product_list),
                    loop
                ).result()

            def get_products_sync():
                return asyncio.run_coroutine_threadsafe(
                    diy_recommendation_product_list.DIYProductList(product_list=product_list).get_products(),
                    loop
                ).result()

            recipes_task = loop.run_in_executor(executor, get_recipes_data_sync)
            products_task = loop.run_in_executor(executor, get_products_sync)

            recipes, products = await asyncio.gather(recipes_task, products_task)
        return recipes, products

    async def get_recipes_data(
            self,
            recipe_names: List[str],
            product_list: List[str]
        ) -> List[Dict[str, Any]]:
        """Generate metadata for recipes.

        Generate ingredients, instructions, and nutritional info
        for each recipe.

        Args:
            recipes: List of recipe names.
            product_list: List of products from recipes generated.
                Used to ground ingredients generated with grocery list.

        Returns:
            List of recipe dictionaries with metadata.
        """
        recipes = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            def run_async_get_recipe_data(recipe_name, product_list):
                async def _get_recipe_data():
                    recipe_data = recipe.Recipe(recipe=recipe_name, product_list=product_list)
                    return await recipe_data.get_recipe_data()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(_get_recipe_data())
                loop.close()
                return result

            loop = asyncio.get_running_loop()
            tasks = [
                loop.run_in_executor(executor, run_async_get_recipe_data, recipe_name, product_list)
                for recipe_name in recipe_names
            ]

            results = await asyncio.gather(*tasks)
            recipes.extend(results)

        return recipes

    async def get_recipe_recommendations(self) -> Tuple[List[str], List[str]]:
        """Get recipe and grocery list recommendation.

        Returns:
            Tuple of recipe names and grocery list for recipes.
        """
        # Prompt to generate recipe and grocery list.
        prompt = prompts.recipes_recommendations_prompt.format(
            user_query=self.query
        )

        # Agent to generate recipes or meal plan.
        diy_agent = diy_recommendations.DIYRecommendations(
            query=self.query,
            prompt=prompt
        )
        result = await diy_agent.get_recommendations()

        recipe_names = result.get("diy_ideas")
        grocery_list = result.get("product_list")

        return (recipe_names, grocery_list)
