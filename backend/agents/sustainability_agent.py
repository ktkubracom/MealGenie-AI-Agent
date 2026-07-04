# agents/sustainability_agent.py
import json
from .api_client import call_api

def analyze_sustainability(recipe_title: str, ingredients: list[str]) -> dict:
    """Use the Sustainability Agent to estimate environmental impact and carbon score."""
    prompt = (
        f"You are an environmental sustainability scientist specializing in food agriculture. "
        f"Analyze this recipe:\n"
        f"Title: {recipe_title}\n"
        f"Ingredients: {', '.join(ingredients)}\n\n"
        "Estimate the carbon footprint (kg CO2 equivalent per serving), water footprint impact, "
        "and assign an environmental score rating (Grade A to F, where A is lowest footprint like local vegan vegetables, "
        "and F is highest like imported beef/lamb). "
        "Also provide a short eco-friendly tip to reduce the footprint further.\n"
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "co2_footprint": "1.2 kg CO2e",\n'
        '  "water_footprint": "Low/Medium/High",\n'
        '  "grade": "B",\n'
        '  "eco_tip": "Replacing butter with olive oil will reduce the carbon footprint by 15%."\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    try:
        res_text = call_api(prompt, json_mode=True)
        data = json.loads(res_text)
        return {
            "co2_footprint": data.get("co2_footprint", "Unknown"),
            "water_footprint": data.get("water_footprint", "Unknown"),
            "grade": data.get("grade", "C").upper(),
            "eco_tip": data.get("eco_tip", "Buy local ingredients when possible.")
        }
    except Exception:
        return {
            "co2_footprint": "1.5 kg CO2e",
            "water_footprint": "Medium",
            "grade": "C",
            "eco_tip": "Buy local ingredients and reduce food waste."
        }
