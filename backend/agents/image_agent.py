import json
from .api_client import call_api

def generate_recipe_image(title: str, ingredients: list[str]) -> str:
    """Generate a food‑image URL for a recipe using a text‑to‑image model.
    Returns a direct image URL (or placeholder) suitable for embedding in HTML.
    """
    prompt = (
        f"Create a photorealistic, high‑resolution food image for this recipe.\n"
        f"Title: {title}\n"
        f"Main ingredients: {', '.join(ingredients)}\n"
        "Return ONLY a direct image URL (no markdown)."
    )
    try:
        # Use the same Gemini endpoint but request non‑JSON mode to get raw URL text
        response = call_api(prompt, json_mode=False)
        return response.strip()
    except Exception:
        # Fallback to a static placeholder image
        return "https://via.placeholder.com/800x600.png?text=Recipe+Image+Unavailable"
