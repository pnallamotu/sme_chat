# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Data models for Chat."""

from pydantic import BaseModel


class ChatModel(BaseModel):
    """Chat Model.

    Properties:
        user_query: Query for a request. 
    """
    user_query: str
