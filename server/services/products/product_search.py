# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Product Search Module."""

import re
from typing import Any, Dict, List

from server.common import gemini
from server.common import prompts
from server.config.logging import logger
from server.functions import vertex_search


class ProductSearch:
    """Module for product search."""
    def __init__(self, query: str):
        """Init product search module.

        Args:
            query: Query used to search for a product.
        """
        self.query = query

        # Vertex search manager to search datastore.
        self.vertex_search_client = vertex_search.VertexSearchManager()

        # Gemini instance to generate category / title.
        self.model = gemini.GeminiModelManager()

    async def get_products(
        self,
    ) -> Dict[str, Any]:
        """Get list of products for a specific type of product.

        E.g: "Apples" or "Hammer".

        Returns:
            Dictionary of summarized title of product names, and list of products.
                E.g. {
                        "title": "Apples",
                        "product_names": [{product_1_dict}, {product_2_dict}]
                    }
        """
        try:
            # Get products from catalog.
            product_recommendations = self.search_product_catalog(self.query)

            # Generate title for products.
            title = await self.generate_products_title(
                products=product_recommendations)
            return {
                "title": title,
                "product_names": product_recommendations
            }
        except Exception as e:
            logger.error(f"Error searching for products: {e}")

    def search_product_catalog(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """Search against datastore.

        Args:
            Query to search against datastore.
        """
        # TODO: update this function if want to use
        # another database to query products from.
        # This currently uses vertex search with a website datastore.
        matched_products = self.vertex_search_client.search(query)

        # TODO: Update for a new customer.
        products = parse_es_result(response=matched_products)
        return products

    async def generate_products_title(self, products: List[Dict[str, Any]]) -> str:
        """Generate a title for the products returned from a search.

        Args:
            List of product dictionaries.

        Returns:
            Title / Category of products in list.
        """

        # TODO: Change based on how catalog results are stored
        # in the function above.
        product_names = [product["title"] for product in products]

        # Insert query and product names into
        # prompt to generate title.
        prompt = prompts.product_title_prompt.format(
            query=self.query,
            products=product_names
        )

        title = await self.model.generate_response(
            contents=prompt,
            temperature=0.2,
            max_output_tokens=30
        )
        return title


async def get_individual_product_type(product_type) -> Dict[str, Any]:
    """Used for parallelization.

    Product search for a product type / category.

    Args:
        product_type: Query to send to Vertex search.
    """
    search = ProductSearch(query=product_type)
    return await search.get_products()


def parse_es_result(response) -> List[Dict[str, Any]]:
    """Parse Vertex Search Results.

    This function is based on a customer's es results.
    Update based on customer website results schema.

    Returns:
        List with product title, url, sku, and image.
    """
    # List of products from vertex search.
    products = []
    
    # TODO: edit to match to customer's es result payload.
    for resp in response.results:
        # Parse product data from ES results.
        product_data = resp.document.derived_struct_data
        try:
            # Get title from metatags else default to
            # main title.
            try:
                # Get title.
                title = product_data["pagemap"].get("metatags")[0].get(
                    "og:title").replace(" - albertsons", "")
            except (KeyError, IndexError, AttributeError):
                title = product_data["title"]

            # Get product url.
            url = product_data["pagemap"].get("metatags")[0].get("og:url")

            # Extract sku from url.
            sku = parse_product_sku(url)

            # NOTE: Vertex search for Walmart & Albertson's did not return price in the response.
            # Thus, we return default price of $5.00 until integration with domain verificaiton
            # or customer's price data.

            # Product title, price, url, sku, and image.
            product_info = {
                "title": title,
                "price": 5.00,
                "url": url,
                "sku": sku,
                "image": product_data["pagemap"].get("cse_image")[0].get("src")
            }
            products.append(product_info)
        except Exception as e:
            logger.error(f"Failed parsing product for {product_data['title']}")
            logger.error(e)
            continue
    return products


def parse_product_sku(url: str) -> int:
    """Parses the product sku from url.

    Args:
        url (str): The URL to parse.

    Returns:
        int or None: The product ID if found, otherwise None.
    """
    match = re.search(r"product-details\.(\d+)\.html", url)
    if match:
        return int(match.group(1))
    else:
        return None
