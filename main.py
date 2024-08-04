# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""FastAPI App."""

import os

from fastapi import FastAPI
import uvicorn

from server.common import utils
from server.routes import chat
from server.routes import saved_recipes


app = FastAPI()


# Env variables for local dev.
ENV = os.getenv("ENV", "DEV")
if ENV == "DEV":
    utils.load_config_to_env("./config.yaml")


# Routes.
app.include_router(chat.router, prefix="/api")
app.include_router(saved_recipes.router, prefix="/api")


if __name__ == "__main__":
    uvicorn.run(app)
