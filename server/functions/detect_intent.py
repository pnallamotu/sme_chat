# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Intent Module."""

from typing import Optional

from server.common import gemini
from server.config.logging import logger
from server.functions import vector_search


class IntentClassifier:
    """Module to classify intent of query."""
    def __init__(
        self,
        system_context: str = None,
        use_vector_db: bool = True
    ):
        """Intializes intent classifer.

        Args:
            system_context: Prompt of intents to classify.
            use_vector_db: Boolean of whether to search against
                Vector database. Used to setup gaurdrails.
        """
        self.system_context = system_context
        self.use_vector_db = use_vector_db

        self.model = gemini.GeminiModelManager(
            system_prompt=system_context
        )

        # Set up vector search manager.
        if self.use_vector_db:
            self.vector_search_client = vector_search.VectorSearchManager()

    async def classify_intent(self, query: str) -> str:
        """Classify intent of query.

        Using gemini to classify intent of a query
        based on system context of the intent llm model.

        Returns:
            intent (str).
        """
        try:
            intent = await self.model.generate_response(
                contents=query,
                max_output_tokens=100,
                temperature=0.5
            )
            return intent
        except Exception as e:
            logger.error(
                f"Error classifying intent for user query: {query}:  {e}")


    def check_malicious_query(
            self,
            query: str,
            threshold: Optional[float]  = 0.22
        ) -> bool:
        """Checks for malicious query.

        Performs search against vector search db
        for similarity against malicious queries.

        Args:
            query: user query.
            threshold: threshold to block a query based on similarity.

        Return:
            Boolean of whether query is malicious (default False).
        """
        try:
            # If a vector search endpoint was set up
            # search against index for malicious similarity.
            if self.use_vector_db:
                nearest_neighbors = self.vector_search_client.query(
                    query=query)

                # Get closest match to query.
                most_similar_match = nearest_neighbors[0]

                # Check if query is malicious based on threshold.
                if most_similar_match.get("distance") >= threshold:
                    return True
            return False
        except Exception as e:
            logger.error(
                f"Error checking whether user query: {query} is malicious: {e}")
            # Defaulting True for gaurdrail
            return True
