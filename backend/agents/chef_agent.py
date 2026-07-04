import json
from .api_client import call_api

def create_recipe(ingredients: list[str], preferences_context: str = "") -> dict:
    """Use the Genie Chef Agent to generate the main recipe incorporating user preferences."""
    prefs_info = f"\nTake into account these user preferences and constraints: {preferences_context}\n" if preferences_context else ""
    prompt = (
        f"You are Genie, a professional AI chef. Create a single, creative, and delicious recipe using some or all of these ingredients: {', '.join(ingredients)}. "
        f"{prefs_info}"
        "You may assume basic kitchen staples (like salt, pepper, oil, water) are available. "
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "title": "A fun, creative recipe title (without cooking emojis at the end)",\n'
        '  "servings": 2,\n'
        '  "ingredients": ["Ingredient 1 (quantity)", "Ingredient 2 (quantity)"],\n'
        '  "steps": [\n'
        '    "Step 1...",\n'
        '    "Step 2...",\n'
        '    "Step 3..."\n'
        '  ],\n'
        '  "tags": ["Tag1", "Tag2"]\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    res_text = call_api(prompt=prompt, json_mode=True)
    recipe = json.loads(res_text)
    return {
        "title": recipe.get("title", "Genie Special"),
        "servings": int(recipe.get("servings", 2)),
        "ingredients": [item.title() for item in recipe.get("ingredients", [])],
        "steps": recipe.get("steps", []),
        "tags": recipe.get("tags", ["AI-Generated"])
    }
