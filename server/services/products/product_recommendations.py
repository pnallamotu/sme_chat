# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Product Recommendations Module."""

from typing import Any, Dict, List

from server.common import gemini
from server.common import prompts
from server.common import utils
from server.services.products import product_search


class ProductRecommendations:
    """Generate product recommendations."""
    def __init__(self, query):
        """Init products recommendations agent

        Args:
            query: User query to get product recs for.
        """
        self.query = query

        # Init product model with system context.
        self.model = gemini.GeminiModelManager(
            system_prompt=prompts.product_recommendations_system_context
        )

    async def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get product recommendations from query.

        Returns:
            List of product recommendations. Where each dictionary
            has a product title/category and it's respective products.
        """
        product_recommendations = []

        # List of categories or product types to search for
        # based on user query.
        product_recs_generated = await self.get_product_types_from_query()

        # For each product type recommended
        # make product search query to catalog.
        product_recommendations = await utils.make_parallel_calls(
            items=product_recs_generated,
            async_processing_func=product_search.get_individual_product_type
        )
        return product_recommendations

    async def get_product_types_from_query(self) -> List[str]:
        """Generate list of product types from query.

        Uses gemini to extract product types or recommendations
        to search for based on user query. These product types
        are used as queries to search against a product catalog.

        Returns:
            List of extracted product names.
        """
        # Insert user query to prompt template.
        prompt = prompts.product_recommendations_prompt_template.format(
            user_query=self.query
        )

        # List of product types for recommendations.
        product_types = await self.model.generate_response(
            contents=prompt,
            max_output_tokens=1000,
            temperature=0.2,
            response_mime_type="application/json"
        )

        return product_types
