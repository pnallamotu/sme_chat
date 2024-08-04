# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""SME Main Agent."""

from typing import Any, Dict, List

from server.common import gemini
from server.common import prompts
from server.config.logging import logger
from server.services.products import product_recommendations
from server.services.products import product_search
from server.services.recipes import recipe_recommendations


class SmeRunner:
    """Model to get results based on intent & query."""
    def __init__(
        self,
        query: str,
        intent: str
    ):
        """Shopping made easy agent runner.

        Process results based on query and intent.

        Args:
            query: Current user query.
            intent: intent of user query.
        """
        self.query = query
        self.intent = intent

        # Gemini instance to summarize results.
        self.model = gemini.GeminiModelManager()

    async def process(self):
        """Process query."""
        logger.info("Processing SME.")

        # Default payload.
        # Filled based on intent.
        products = []
        recipes = []
        msg = None
        intent = self.intent

        # TODO: Update if need to change intent names.
        # or want to add more intents.
        if self.intent == "generic_product_search":
            logger.info("In product search intent.")
            product_search_result = await product_search.ProductSearch(
                query=self.query
            ).get_products()

            # Products should be an array of product categories.
            # For specific search it will just be one category, but payload
            # should be a list of product categories.
            products = [product_search_result]
        elif self.intent == "product_recommendations":
            logger.info("In product recs intent.")
            products = await product_recommendations.ProductRecommendations(
                query=self.query
            ).get_recommendations()

        elif self.intent == "recipes":
            logger.info("In recipes intent.")
            recipes, products = await recipe_recommendations.RecipeRecommendations( # pylint: disable=line-too-long
                query=self.query
            ).get_recommendations()


        result = {
            "products": products,
            "recipes": recipes,
        }

        # Summarize result for message to display.
        msg = await self.summarize_result(result=result)

        # Update payload with msg and intent.
        result.update({
            "msg": msg,
            "intent": intent
        })

        return result

    async def summarize_result(self, result):
        """Summarize result for a message."""
        logger.info("Summarizing result.")
        products =  result.get("products")
        recipes = result.get("recipes")
        result_for_prompt = {}

        # Extract just product names.
        if products:
            product_names = self.get_product_names(products=products)
            result_for_prompt["products"] = product_names

        if recipes:
            recipe_names = self.get_recipe_names(recipes=recipes)
            result_for_prompt["recipes"] = recipe_names

        # Format prompt with result.
        # If products or recipes is empty list,
        # the prompt will insert an empty list to summarize.
        prompt = prompts.summarize_result_prompt.format(
            query=self.query,
            result=result_for_prompt
        )

        msg = await self.model.generate_response(
            prompt,
            max_output_tokens=200,
            temperature=0.2
        )
        return msg

    def get_product_names(self, products: List[Dict[str, Any]]) -> List[str]:
        """Get product names from list of product results.

        From a list of product names, get only product names.
        Used for summarizing the result to a user.

        Args:
            products: List of product dictionaries.
                Each dictionary is a product category with multiple
                product names.
        """
        product_names = []
        for category in products:
            products_in_category = [
                product["title"]
                for product in category.get("product_names")
            ]
            product_names.extend(products_in_category)
        return product_names


    def get_recipe_names(self, recipes: List[Dict[str, Any]]) -> List[str]:
        """Get recipe names from list of recipe results.

        From a list of recipe names, get only recipe names.
        Used for summarizing the result to a user.

        Args:
            products: List of product dictionaries.
                Each dictionary is a product category with multiple
                product names.
        """
        recipe_names = []
        for recipe in recipes:
            recipe_names.append(recipe.get("name"))
        return recipe_names
