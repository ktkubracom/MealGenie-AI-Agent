import time
from agents.genie_agent import genie_generate
from utils.cache_manager import get_cached_recipe, set_cached_recipe
from utils.logger import log_performance, log_error
from utils.security import sanitize_text


def process_input(raw_text: str, preferences: dict = None) -> dict:
    """
    Orchestrates recipe generation through Genie, the master AI agent.

    Genie handles everything in ONE API call:
      - Recipe creation (Chef role)
      - Safety and allergen verification (Safety Inspector role)
      - Nutrition estimation (Nutritionist role)
      - Ingredient substitutes and upgrades (Pantry Advisor role)
      - Drink pairing (Sommelier role)
      - Eco impact scoring (Sustainability Expert role)

    Caching ensures repeated requests skip the API entirely.
    """
    start_time = time.time()
    if preferences is None:
        preferences = {}

    cached = get_cached_recipe(raw_text, preferences)
    if cached:
        duration = time.time() - start_time
        log_performance("process_input (CACHE HIT)", duration, f"Ingredients: {raw_text[:40]}")
        return cached

    sanitized_input = sanitize_text(raw_text)

    try:
        result = genie_generate(ingredients=sanitized_input, preferences=preferences)
    except Exception as e:
        log_error("Genie generate", str(e))
        raise ValueError(str(e))

    try:
        set_cached_recipe(raw_text, preferences, result)
    except Exception as cache_err:
        log_error("Cache Save", str(cache_err))

    duration = time.time() - start_time
    log_performance("process_input (CACHE MISS)", duration, f"Ingredients: {raw_text[:40]}")
    return result


def generate_full_recipe(user_id: str, ingredients: list, preferences: dict = None) -> str:
    """FastAPI-compatible wrapper. Used by backend/api/routes.py."""
    ingredients_str = ", ".join(ingredients) if isinstance(ingredients, list) else str(ingredients)
    result = process_input(ingredients_str, preferences or {})
    lines = [f"# {result.get('display_title', 'Recipe')}"]
    lines.append(f"\n**Servings:** {result.get('servings', 2)}")
    lines.append("\n## Ingredients")
    for ing in result.get("ingredients", []):
        lines.append(f"- {ing}")
    lines.append("\n## Instructions")
    for step in result.get("steps", []):
        lines.append(str(step))
    lines.append(f"\n*{result.get('note', '')}*")
    return "\n".join(lines)
