# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""DIY Recommendation data generation module."""

from typing import Any, Dict
import uuid

from server.common import gemini


class DIYRecommendation:
    """Generate metadata for a DIY recommendation.

    For any intent queries that relate to a user
    looking for DIY ideas recipes, home improvement ideas, etc.).
    It will use a prompt to generate additional metadata.
    """
    def __init__(
        self,
        diy_idea: str,
        prompt: str
    ):
        """Init DIY Recommendation metadata generation.

        Args:
            diy_idea: string of idea name (recipe name, etc.)
            prompt: Prompt of context of metadata to generate.
        """
        self.diy_idea = diy_idea

        self.model = gemini.GeminiModelManager()
        self.prompt = prompt

    async def generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata for diy idea.

        Returns dictionary of original idea name
        and additional metadata specified by prompt.
        """
        # Generate DIY
        result = await self.model.generate_response(
            contents=self.prompt,
            temperature=0.3,
            max_output_tokens=8192,
            response_mime_type="application/json"
        )

        # Generate unique id for idea.
        result_id = generate_id()

        # Get youtube video for idea.
        yt_url = get_youtube_url(self.diy_idea)

        result.update({
            "name": self.diy_idea,
            "id": result_id,
            "yt_url": yt_url
        })

        return result


def generate_id() -> int:
    """Generates a unique id

    Return:
        Integer id.
    """
    full_uuid_int = uuid.uuid4().int
    generated_id = full_uuid_int % 10**10
    return generated_id


def get_youtube_url(query: str) -> str:
    """Get a Youtube video url.

    Args:
        query: Youtube API search query.

    Returns:
        First found youtube url.
    """
    # TODO: Uncomment when showing to customer
    # or for production. Commented for quota reasons.
    try:
        return "https://www.youtube.com/"
        # api_key = os.getenv("api_key")
        # youtube_client = build("youtube","v3",developerKey = api_key)
        # request = youtube_client.search().list(
        #     q=query,
        #     part="snippet",
        #     type="video",
        #     maxResults=1
        # )
        # response = request.execute()

        # if response["items"]:
        #     first_video = response["items"][0]
        #     video_id = first_video["id"]["videoId"]
        #     video_url = f"https://www.youtube.com/watch?v={video_id}"
        #     return video_url
        # else:
        #     return "https://www.youtube.com/"
    except Exception:
        return "https://www.youtube.com/"
