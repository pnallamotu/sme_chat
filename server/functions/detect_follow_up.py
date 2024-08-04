# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Follow Up Module."""

from typing import Any, Dict, List

from server.common import gemini
from server.common import prompts
from server.config.logging import logger


class FollowUpClassifier:
    """Module to classify if query is follow up."""
    def __init__(
        self,
        query: str,
        history: List[Dict[str, Any]]
    ):
        """Intializes follow up classifier.

        Args:
            query: Current user query.
            history: Chat history.
        """
        self.query = query
        self.history = history

        self.model = gemini.GeminiModelManager()

    async def classify_follow_up(self) -> str:
        """Classify if query is follow_up

        Returns:
            boolean if follow up.
        """
        try:
            if self.history:
                # We only care about the last response and message.
                prompt = prompts.follow_up_classifier_prompt.format(
                    history=self.history[-1],
                    query=self.query
                )
                is_follow_up = await self.model.generate_response(
                    contents=prompt,
                    max_output_tokens=100,
                    temperature=0.0
                )
                # TODO (pnallamotu): clean this up.
                return is_follow_up.lower() == "true"
            return False
        except Exception as e:
            logger.error(
                f"Error classifying whether query is follow up, defaulting to False")
            return False

    async def summarize_follow_up_query(self) -> str:
        """Transform query for follow up.

        Use the last turn and current query to craft a
        new query to send to a turn.

        Returns:
            Query summarzing follow up query with respect to
            last query and response.
        """
        prompt = prompts.multi_turn_query_system_prompt.format(
            history=self.history[-1],
            query=self.query
        )
        transformed_query = await self.model.generate_response(
            contents=prompt,
            max_output_tokens=500,
            temperature=0.0
        )
        return transformed_query
