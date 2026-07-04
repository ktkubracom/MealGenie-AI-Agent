import json
from .api_client import call_api

def suggest_pairing(recipe_title: str, tags: list[str]) -> dict:
    """Use the Sommelier Agent to suggest food pairings via the API."""
    prompt = (
        f"You are a professional sommelier. Given this recipe:\n"
        f"Title: {recipe_title}\n"
        f"Tags: {', '.join(tags)}\n\n"
        "Recommend one alcoholic drink pairing and one non-alcoholic drink pairing that fit this dish perfectly. Provide a very brief explanation why. "
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "alcoholic": "Drink Name - short explanation",\n'
        '  "non_alcoholic": "Drink Name - short explanation"\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    try:
        res_text = call_api(prompt, json_mode=True)
        data = json.loads(res_text)
        return {
            "alcoholic": data.get("alcoholic", "White wine"),
            "non_alcoholic": data.get("non_alcoholic", "Sparkling water")
        }
    except Exception:
        # Graceful fallback
        return {
            "alcoholic": "Amber Ale",
            "non_alcoholic": "Lemonade"
        }
