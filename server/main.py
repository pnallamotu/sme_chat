# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""FastAPI App."""

import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

from server.common import utils
from server.config.logging import logger
from server.models import chat
from server.turns import turn


app = FastAPI()


# Env variables for local dev.
ENV = os.getenv("ENV", "DEV")
if ENV == "DEV":
    utils.load_config_to_env("./config.yaml")


@app.post("/api/send-message")
async def send_message(request: Request):
    try:
        logger.info('API is starting up')
        data = await request.json()

        # Set user query.
        user_query = chat.ChatModel(**data).user_query

        result = await turn.Turn().process(query=user_query)

        # await some_async_message_sending_function()
        return JSONResponse(result)
    except Exception as e:
        logger.error('API is starting up')
        return JSONResponse({"msg": "Error"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
