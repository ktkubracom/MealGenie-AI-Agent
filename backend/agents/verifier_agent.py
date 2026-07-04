import json
from .api_client import call_api

def verify_ingredients(ingredients: list[str], preferences: dict) -> tuple[list[str], list[str]]:
    """Use the Verifier Agent to filter ingredients and generate warnings based on preferences via the API."""
    diet = preferences.get("diet", "")
    allergies = preferences.get("allergies", [])
    dislikes = preferences.get("dislikes", [])
    summary = preferences.get("summary", "")
    
    # If no preferences are set, skip API call to save resources
    if not diet and not allergies and not dislikes:
        return ingredients, []
        
    prompt = (
        f"You are a food safety verifier agent. Given these input ingredients: {', '.join(ingredients)}\n"
        f"Dietary restriction: {diet}\n"
        f"Allergies: {', '.join(allergies)}\n"
        f"Dislikes: {', '.join(dislikes)}\n"
        f"User Modification Context: {summary}\n\n"
        "Filter out any ingredients that violate the dietary restriction, are unsafe due to allergies, or are explicitly in the Dislikes list. "
        "CRITICAL EXCEPTION: If the 'User Modification Context' explicitly requests the inclusion of a restricted or disliked ingredient, you MUST allow it and not filter it out. "
        "Generate brief, helpful warning messages explaining what was removed or flagged, or if an exception was made. "
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "filtered_ingredients": ["safe_ingredient_1", "safe_ingredient_2"],\n'
        '  "messages": ["Warning message 1", "Warning message 2"]\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    try:
        res_text = call_api(prompt, json_mode=True)
        data = json.loads(res_text)
        return (
            data.get("filtered_ingredients", ingredients),
            data.get("messages", [])
        )
    except Exception:
        # Graceful fallback: return original ingredients, and a network warning
        return ingredients, ["Verification check was bypassed due to a network connection issue."]
