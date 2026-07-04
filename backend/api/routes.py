from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.recipe_gecp_server import generate_full_recipe

router = APIRouter()

class RecipeRequest(BaseModel):
    user_id: str
    ingredients: List[str]
    preferences: Optional[dict] = None

class RecipeResponse(BaseModel):
    recipe_markdown: str

@router.post("/generate_recipe", response_model=RecipeResponse)
def generate_recipe(req: RecipeRequest):
    try:
        # Calls the existing AI Swarm orchestrator
        # Assuming generate_full_recipe takes user_id, ingredients, preferences
        result = generate_full_recipe(req.user_id, req.ingredients, req.preferences)
        return RecipeResponse(recipe_markdown=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
