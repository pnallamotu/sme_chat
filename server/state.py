# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""Local Chat history."""

# TODO: Edit to use Memorystore or Redis in production instead.
# Currently used for multi-turn for POC.
message_history = []
