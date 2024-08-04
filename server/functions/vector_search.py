# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Vector Search Module."""

import os
from typing import Any, Dict, List, Optional

from google.cloud import aiplatform
from vertexai.preview.language_models import (
   TextEmbeddingInput,
   TextEmbeddingModel
)


class VectorSearchManager:
    """Vertex Search Module."""
    def __init__(
        self,
        index_endpoint_id: Optional[str] = None,
        index_endpoint_name: Optional[str] = None
    ):
        """Init Vector Search client.

        Args:
            index_endpoint_id: Vector Search endpoint id.
            index_endpoint_name: Vector Search endpoint name.
        """

        # Vector search endpoint.
        endpoint_id = index_endpoint_id or os.getenv("vector_search_id")
        self.index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            endpoint_id)

        # Endpoint version / name.
        self.index_endpoint_name = index_endpoint_name or os.getenv(
            "vector_search_endpoint_name")

    def query(
        self,
        query: str,
        top_n_neighbors: Optional[int] = 10
    ) -> List[Dict[str, Any]]:
        """Get top N similar matches from query.

        Args:
            query: User query to search against.
            top_n_neighbors: Number of neighbors to search for.

        Returns:
            List of documents with id and distance.
        """
        # Embed query.
        embedded_query = self.embed_text(query)

        # Get nearest neighbors.
        similar_matches = self.find_neighbors(
            embedded_query,
            top_n_neighbors
        )
        return similar_matches

    def embed_text(
        self,
        query: str,
        task: str = "SEMANTIC_SIMILARITY",
        model_name: str = "text-embedding-004",
        dimensionality: Optional[int] = 256,
    ) -> List[List[Any]]:
        """Embeds a list of texts.

        Args:
            query: The query to embed.
            task: The task for which the embeddings will be used.
            model_name: The name of the pre-trained text embedding model to use.
            dimensionality: The desired dimensionality of the embeddings. If None, the
                default dimensionality of the model is used.

        Returns:
            A list of lists, where each inner list represents the emebddings of a text.
        """
        model = TextEmbeddingModel.from_pretrained(model_name)
        inputs = [TextEmbeddingInput(query, task)]
        kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
        result = model.get_embeddings(inputs, **kwargs)
        return [e.values for e in result]

    def find_neighbors(
        self,
        embedded_text: List[List[Any]],
        num_neighbors: int
    ) -> List[Dict[str, Any]]:
        """Get nearest neighbors.

        Args:
            embedded_text: Query to search against.
            num_neighbors: Number of neighbors to return.

        Returns:
            List of documents with id and distance.
        """
        response = self.index_endpoint.find_neighbors(
            deployed_index_id=self.index_endpoint_name,
            queries=embedded_text,
            num_neighbors=num_neighbors,
        )

        # Get most similar match ids with distances.
        similar_matches = []
        for _, neighbor in enumerate(response[0]):
            similar_matches.append({
                "id": int(neighbor.id),
                "distance": neighbor.distance
            })
        return similar_matches
