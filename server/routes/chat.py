# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""API Routes for chat."""

import base64
import os

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from vertexai.generative_models import Part

from server.common import utils
from server.config.logging import logger
from server.models import chat
from server.state import message_history
from server.turns import multi_turn
from server.services.image import sme_images

router = APIRouter()


@router.post("/send-message")
async def send_message(request: Request):
    try:
        logger.info("Sending chat message")
        data = await request.json()

        # Set user query.
        user_query = chat.ChatModel(**data).user_query

        result = await multi_turn.MultiTurn(
            query=user_query,
            history=message_history
        ).process()

        message_history.append({
            "user_query": user_query,
            "response": result
        })

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error making request: {e}")
        return JSONResponse({"msg": "Error"})


@router.post("/send-message/image")
async def send_image(image: UploadFile = File(...)):
    try:
        logger.info("Image input to chat")
        if not image:
            raise

        contents = await image.read()

        # Convert image to gemini part.
        encoded_image = base64.b64encode(contents).decode("utf-8")
        image_content = Part.from_data(
            data=base64.b64decode(encoded_image),
            mime_type=image.content_type
        )

        # Convert image to query matching intents. 
        user_query = await sme_images.SMEImages(image_contents=image_content).process_image()

        result = await multi_turn.MultiTurn(
            query=user_query,
            history=message_history
        ).process()

        message_history.append({
            "user_query": user_query,
            "response": result
        })

        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error making request: {e}")
        return JSONResponse({"msg": "Error"})