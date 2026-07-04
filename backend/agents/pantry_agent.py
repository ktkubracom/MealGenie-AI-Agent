import json
from .api_client import call_api

def suggest_substitutes(recipe_title: str, ingredients: list[str]) -> dict:
    """Use the Pantry Agent to suggest replacements and upgrades via the API."""
    prompt = (
        f"You are a smart kitchen pantry assistant. Given this recipe:\n"
        f"Title: {recipe_title}\n"
        f"Ingredients: {', '.join(ingredients)}\n\n"
        "Suggest common, intelligent substitutions for the main ingredients in the recipe (up to 3 ingredients). "
        "Also suggest 2 creative upgrades/twists (e.g. spices, herbs, toppings) to elevate the dish. "
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "substitutes": {\n'
        '    "ingredient_name": ["substitute_option_1", "substitute_option_2"]\n'
        '  },\n'
        '  "upgrades": ["upgrade suggestion 1", "upgrade suggestion 2"]\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    try:
        res_text = call_api(prompt, json_mode=True)
        data = json.loads(res_text)
        return {
            "substitutes": data.get("substitutes", {}),
            "upgrades": data.get("upgrades", [])
        }
    except Exception:
        # Graceful fallback
        return {
            "substitutes": {},
            "upgrades": ["Fresh herbs", "A pinch of red pepper flakes"]
        }
