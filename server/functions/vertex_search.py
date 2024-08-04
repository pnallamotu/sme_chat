# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Vertex Search Module."""

import os
from typing import Optional

from google.cloud import discoveryengine_v1 as discoveryengine


class VertexSearchManager:
    """Vertex Search Module."""
    def __init__(
        self,
        project_number: Optional[str] = None,
        location: Optional[str] = "global",
        data_store_id: Optional[str] = None,
        serving_config_id: Optional[str] = None
    ):
        # Vertex search config params.
        self.project_number = project_number or os.getenv("project_number")
        self.location = location or os.getenv("es_search_location")
        self.data_store_id = data_store_id or os.getenv(
            "es_search_data_store_id")
        self.serving_config_id = serving_config_id or os.getenv(
            "es_search_serving_config_id")

        # Init vertex search config.
        self.serving_config = self._init_search_client()

        # Vertex search client.
        self.client = discoveryengine.SearchServiceClient()

    def _init_search_client(self) -> str:
        """Initialize a Vertex Search config."""
        serving_config = f"projects/{self.project_number}/locations/{self.location}/"\
            f"collections/default_collection/dataStores/{self.data_store_id}/"\
            f"servingConfigs/{self.serving_config_id}"
        return serving_config

    def search(self, query: str, page_size: int = 10):
        """Perform a Vertex Search.

        Args:
            query: Search query.
            page_size: Number of max results.

        Returns:
            Vertex search matched documents.
        """
        # Create request object.
        request = discoveryengine.SearchRequest(
            serving_config=self.serving_config,
            query=query,
            page_size=page_size,
        )

        response = self.client.search(request)
        return response
