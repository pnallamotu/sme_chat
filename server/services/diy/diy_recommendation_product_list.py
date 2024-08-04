# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""DIY Idea product list."""

from typing import Any, Dict, List

from server.common import utils
from server.services.products import product_search


class DIYProductList:
    """Maps DIY idea product list to catalog."""
    def __init__(self, product_list: List[str]):
        """Init DIY Product List mapping.

        Map the generated product list needed from diy
        ideas to product catalog using the product search
        service.

        Args:
            product_list: Generated product list from ideas.
        """
        self.product_list = product_list

    async def get_products(self) -> List[Dict[str, Any]]:
        """Returns products from catalog.

        Returns:
            List of products mapped to catalog
            from generated product names needed for idea.
                (E.g Apple -> mapped to catalog).
        """
        # For each product needed
        # make product search query to catalog.
        products = await utils.make_parallel_calls(
            items=self.product_list, async_processing_func=product_search.get_individual_product_type)

        return products
