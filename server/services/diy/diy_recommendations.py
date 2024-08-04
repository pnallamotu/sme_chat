# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""DIY Recommendations Module."""

from server.common import gemini


class DIYRecommendations:
    """Generate Do it yourself recommedations.

    For any intent queries that relate to a user
    looking for DIY ideas.
        For example (recipes, home improvement ideas, etc.).
    """
    def __init__(
        self,
        query: str = None,
        prompt: str = None
    ):
        """Init DIY Agent.

        Args:
            query: User query to generate DIY ideas / product list for.
        """
        self.query = query

        self.model = gemini.GeminiModelManager()
        self.prompt = prompt


    async def get_recommendations(self):
        """Get DIY recommendations.

        Returns:
            Dictionary of DIY ideas and prodcuts.
            E.g: grocery list, home improvement ideas, etc.
                - diy_name is a list of each diy name.
                - products is the product list needed for all the diy ideas.
        """
        # Generate DIY idea names & whole product list together.
        result = await self.model.generate_response(
            contents=self.prompt,
            temperature=0.5,
            max_output_tokens=8192,
            response_mime_type="application/json"
        )
        return result
