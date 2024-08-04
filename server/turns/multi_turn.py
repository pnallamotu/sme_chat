# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Multi Turn."""

import traceback
from typing import Any, Dict, List

from server.common import prompts
from server.config.logging import logger
from server.functions import detect_follow_up
from server.turns import turn


class MultiTurn:
    """Module to orchestrate multi-turn

    Includes the following steps:
        1. Check whether query is a follow-up to previous query.
        2a. If follow up, summarize last turn and rephrase query.
        2b. If not follow up, continue to turn with current query.
    """
    def __init__(
        self,
        query: str,
        history: Dict[str, Any]
    ):
        """Init multi-turn.

        Args:
            history: History of current session - last query and response.
        """
        self.query = query
        self.history = history
        self.follow_up_classifier = detect_follow_up.FollowUpClassifier(
            history=self.history,
            query=self.query
        )

    async def process(self):
        """Runner for turn orchestration."""
        try:
            is_follow_up = await self.follow_up_classifier.classify_follow_up()

            logger.info(f"Follow up: {is_follow_up}")

            # Summarize follow up query using history.
            if is_follow_up:
                self.query = await self.follow_up_classifier.summarize_follow_up_query()
                logger.info(f"Summarized follow up query: {self.query}")

            result = await turn.Turn().process(query=self.query)

            return result
        except Exception as e:
            logger.error(
                f"Error processing query: {self.query}. Defaulting to default payload. {e}")
            traceback.print_exc()
            return {
                "msg": "Sorry I could not process that. Please try re-phrasing your query.",
                "products": [],
                "recipes": [],
                "intent": None
            }
