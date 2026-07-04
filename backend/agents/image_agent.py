# agents/image_agent.py
"""
Generates a food image URL for a recipe.
Uses Unsplash Source API — free, no API key, always returns a real food photo.
Zero API calls to Gemini, zero rate limit risk.
"""

import urllib.parse


def generate_recipe_image(title: str, ingredients: list[str]) -> str:
    """
    Return a food photo URL for the given recipe title.

    Uses Unsplash Source (source.unsplash.com) which picks a random high-quality
    food photo matching the search query. No API key required.

    Args:
        title: recipe title (used as the primary search query)
        ingredients: list of ingredients (top 2 used as fallback keywords)

    Returns:
        A direct image URL string.
    """
    # Build a search query from the recipe title + top ingredients
    keywords = [title]
    if ingredients:
        keywords += [ing.split("(")[0].strip() for ing in ingredients[:2]]

    query = " ".join(keywords[:3])  # keep it concise for better results
    encoded_query = urllib.parse.quote(query)

    # Unsplash Source: returns a random photo matching the query (800x600)
    return f"https://source.unsplash.com/800x600/?food,{encoded_query}"
