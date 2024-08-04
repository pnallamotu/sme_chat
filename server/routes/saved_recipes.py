# Copyright 2024 Google LLC. This software is provided as-is, without warranty
# or representation for any use or purpose. Your use of it is subject to your
# agreement with Google.
"""API Routes for saved recipes."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from server.config.logging import logger
from server.services.recipes import saved_recipes

router = APIRouter()


@router.get("/saved-recipes")
async def get_saved_recipes():
    try:
        logger.info("Getting saved recipes")
        result = saved_recipes.SavedRecipes().get_saved_recipes()
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error getting saved recipes: {e}")
        return JSONResponse({"msg": "Error"})


@router.delete("/saved-recipes/{recipe_id}")
async def delete_saved_recipe(recipe_id: int):
    try:
        logger.info("Deleted saved recipe")
        saved_recipes.SavedRecipes().unsave_recipe(recipe_id=recipe_id)
        return JSONResponse({"msg": "Recipe unsaved."})
    except Exception as e:
        logger.error(f"Error deleting recipe: {e}")
        return JSONResponse({"msg": "Error"})


@router.post("/saved-recipes")
async def save_recipe(request: Request):
    try:
        logger.info("Saving recipe")
        data = await request.json()
        recipe = data.get("recipe")
        await saved_recipes.SavedRecipes().add_saved_recipe(
            recipe=recipe
        )
        return JSONResponse({"msg": "Recipe saved."})
    except Exception as e:
        logger.error(f"Error deleting recipe: {e}")
        return JSONResponse({"msg": "Error"})
