# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Single Turn."""

from server.common import prompts
from server.config.logging import logger
from server.functions import detect_intent
from server.services import sme


class Turn:
    """Module to orchestrate a turn.

    A turn includes the following steps:
        1. Check whether query is malicious.
        2. If false, classify intent.
        3. Return response based on intent.
    """
    def __init__(
        self
    ):
        """Init a turn."""
        # Intent classifier.
        self.intent_classifer = detect_intent.IntentClassifier(
            system_context=prompts.intent_classifer_system_prompt)

    async def process(self, query: str):
        """Runner for turn orchestration."""
        # Check whether query is malicious.
        is_malicious = self.intent_classifer.check_malicious_query(query)

        # Only process queries that are not malicious.
        # Otherwise return default result.
        if not is_malicious:
            intent = await self.intent_classifer.classify_intent(query)
            logger.info(f"Intent for query: {intent}")

            # Process results based on intent & query.
            result = await sme.SmeRunner(
                query=query,
                intent=intent
            ).process()

            return result
