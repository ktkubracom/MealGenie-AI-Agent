import json
from .api_client import call_api

def analyze_nutrition(recipe_title: str, ingredients: list[str]) -> dict:
    """Use the Nutritionist Agent to estimate exact macros and dietary tags via the API."""
    prompt = (
        f"You are a professional nutritionist. Analyze this recipe:\n"
        f"Title: {recipe_title}\n"
        f"Ingredients: {', '.join(ingredients)}\n\n"
        "Estimate the total macronutrients for the entire recipe (in grams, calories in kcal). "
        "Determine applicable dietary labels (e.g. Vegetarian, Vegan, Gluten-Free, Dairy-Free, Low-Carb). "
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "totals": {\n'
        '    "calories": 450,\n'
        '    "protein": 15,\n'
        '    "carbs": 55,\n'
        '    "fat": 12\n'
        '  },\n'
        '  "tags": ["Vegan", "Gluten-Free"]\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    try:
        res_text = call_api(prompt, json_mode=True)
        data = json.loads(res_text)
        return {
            "totals": data.get("totals", {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}),
            "tags": data.get("tags", [])
        }
    except Exception:
        # Graceful fallback on network/parsing issues
        return {
            "totals": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0},
            "tags": ["Standard"]
        }
