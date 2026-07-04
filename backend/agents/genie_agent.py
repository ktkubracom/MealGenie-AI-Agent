# agents/genie_agent.py
"""
Genie — The Master AI Agent for MealGenie.

Genie is a real LLM-powered agent (not rule-based). He talks to the user,
understands their preferences, and when asked to generate a recipe, he acts
as ALL specialists at once: Chef, Nutritionist, Pantry Advisor, Sommelier,
Sustainability Scientist, and Safety Checker — all in a single API call.

Two public functions:
  - genie_chat(...)     → 1 API call — conversational response
  - genie_generate(...) → 1 API call — full recipe JSON with all enrichment
  - genie_extract_preferences(...) → 1 API call — structured preference extraction
"""

import json
from .api_client import call_api


# ---------------------------------------------------------------------------
# CHAT — Genie talks to the user and gathers their preferences naturally
# ---------------------------------------------------------------------------

def genie_chat(ingredients: str, chat_history: list, user_profile: dict) -> str:
    """
    Genie responds to the user's message in a conversational manner.
    He asks smart questions to gather preferences before recipe generation.

    Args:
        ingredients: comma-separated ingredient string (or "surprise me")
        chat_history: list of {"role": "user"/"assistant", "content": str}
        user_profile: dict with allergies, diet, likes, dislikes from Firebase

    Returns:
        Genie's reply as a plain string.
    """
    allergies = ", ".join(user_profile.get("allergies", [])) or "none"
    diet = user_profile.get("diet", "") or "no specific diet"
    likes = ", ".join(user_profile.get("likes", [])) or "none noted"
    dislikes = ", ".join(user_profile.get("dislikes", [])) or "none noted"

    ing_text = (
        f"using: {ingredients}" if ingredients and ingredients.lower() != "surprise me"
        else "with whatever ingredients they have (surprise them!)"
    )

    system_instruction = (
        f"You are Genie, a warm, witty, and expert AI kitchen chef. "
        f"The user wants to make a recipe {ing_text}.\n\n"
        f"What you know about this user:\n"
        f"  - Allergies: {allergies}\n"
        f"  - Diet preference: {diet}\n"
        f"  - Likes: {likes}\n"
        f"  - Dislikes: {dislikes}\n\n"
        f"Your job is to have a natural conversation and learn what they want. "
        f"Ask about things like cook time, cuisine style, equipment, serving size, "
        f"or spice level — one question at a time, naturally. "
        f"Once you have gathered enough context (2-4 turns), enthusiastically tell them "
        f"to click 'Generate Custom Recipe' in the sidebar to bring their dish to life!\n\n"
        f"Rules:\n"
        f"1. Always acknowledge their last message directly before asking anything.\n"
        f"2. Ask only ONE question per reply.\n"
        f"3. Never repeat a question that has already been asked.\n"
        f"4. Be warm, playful, and Genie-like — not robotic or clinical.\n"
        f"5. If the user seems ready (has given ingredients + 1-2 prefs), guide them to generate."
    )

    try:
        response = call_api(
            json_mode=False,
            system_instruction=system_instruction,
            messages=chat_history[-15:]
        )
        return response.strip()
    except Exception as e:
        return f"Oops, my magic is fizzling! An error occurred: {e}"


# ---------------------------------------------------------------------------
# GENERATE — Genie acts as all specialists in one comprehensive LLM call
# ---------------------------------------------------------------------------

def genie_generate(ingredients: str, preferences: dict) -> dict:
    """
    Genie generates a complete, enriched recipe in a single API call.
    He acts as: Chef + Nutritionist + Pantry Advisor + Sommelier +
                Sustainability Scientist + Safety Inspector.

    Args:
        ingredients: comma-separated ingredient string
        preferences: dict with keys: diet, allergies, likes, dislikes, summary

    Returns:
        A fully populated recipe dict ready for the UI to render.

    Raises:
        ValueError: if Genie fails to generate the recipe after retries.
    """
    diet = preferences.get("diet", "") or "no specific diet"
    allergies = preferences.get("allergies", [])
    allergies_str = ", ".join(allergies) if allergies else "none"
    likes = ", ".join(preferences.get("likes", [])) or "none"
    dislikes = ", ".join(preferences.get("dislikes", [])) or "none"
    extra_context = preferences.get("summary", "") or "no extra context"

    prompt = (
        "You are Genie — a master AI chef and multi-disciplinary food expert. "
        "You are generating a complete recipe package for a user.\n\n"
        "=== USER INPUTS ===\n"
        f"Available Ingredients: {ingredients}\n"
        f"Diet Preference: {diet}\n"
        f"Allergies (MUST AVOID — critical): {allergies_str}\n"
        f"Likes: {likes}\n"
        f"Dislikes: {dislikes}\n"
        f"Extra Context / Requests: {extra_context}\n\n"
        "=== YOUR TASK ===\n"
        "You are simultaneously acting as ALL of the following experts. "
        "Produce ONE comprehensive JSON object:\n\n"
        "1. CHEF: Create a creative, delicious recipe using the provided ingredients. "
        "Strictly avoid any allergens. Respect the diet preference. "
        "Format each step with a fun action emoji prefix (use: 🔪 🍳 🧂 ✨ 🫕 🥄 🔥 cycling through). "
        "The display_title must start with \"Genie's Special \" and end with a fitting food emoji.\n\n"
        "2. SAFETY INSPECTOR: Review your own recipe for allergen violations and diet conflicts. "
        "Populate 'warnings' with any issues found. Set 'safety_passed' to true if clean.\n\n"
        "3. NUTRITIONIST: Estimate total macros for the whole recipe "
        "(calories in kcal, protein/carbs/fat in grams). List applicable diet labels.\n\n"
        "4. PANTRY ADVISOR: Suggest smart substitutes for up to 3 main ingredients "
        "(2 options each). Suggest 2 creative upgrades or twists to elevate the dish.\n\n"
        "5. SOMMELIER: Recommend one alcoholic and one non-alcoholic drink pairing "
        "with a brief reason why it works with this dish.\n\n"
        "6. SUSTAINABILITY EXPERT: Estimate CO2 footprint per serving (kg CO2e), "
        "water footprint (Low/Medium/High), eco grade (A=best, F=worst), "
        "and one specific, actionable eco tip.\n\n"
        "=== OUTPUT FORMAT ===\n"
        "Return ONLY valid raw JSON matching this exact schema (no markdown, no code blocks):\n"
        "{\n"
        '  "title": "Recipe title without emojis",\n'
        '  "display_title": "Genie\'s Special [Title] [emoji]",\n'
        '  "servings": 2,\n'
        '  "ingredients": ["Ingredient 1 (quantity)", "Ingredient 2 (quantity)"],\n'
        '  "steps": ["🔪 Step 1...", "🍳 Step 2...", "✨ Step 3..."],\n'
        '  "tags": ["Tag1", "Tag2"],\n'
        '  "note": "A warm, encouraging closing message from Genie.",\n'
        '  "safety_passed": true,\n'
        '  "warnings": [],\n'
        '  "nutrition": {"calories": 450, "protein": 15, "carbs": 55, "fat": 12},\n'
        '  "diet_tags": ["Vegan", "Gluten-Free"],\n'
        '  "substitutes": {"IngredientName": ["option_1", "option_2"]},\n'
        '  "upgrades": ["Creative upgrade 1", "Creative upgrade 2"],\n'
        '  "pairing": {\n'
        '    "alcoholic": "Drink name — brief reason",\n'
        '    "non_alcoholic": "Drink name — brief reason"\n'
        '  },\n'
        '  "sustainability": {\n'
        '    "co2_footprint": "1.2 kg CO2e",\n'
        '    "water_footprint": "Medium",\n'
        '    "grade": "B",\n'
        '    "eco_tip": "One specific actionable tip."\n'
        '  }\n'
        "}"
    )

    try:
        res_text = call_api(prompt=prompt, json_mode=True)
        data = json.loads(res_text)
        return _validate_and_normalize(data)
    except Exception as e:
        raise ValueError(f"Genie failed to generate the recipe: {e}")


# ---------------------------------------------------------------------------
# EXTRACT PREFERENCES — Genie reads the chat and pulls structured prefs
# ---------------------------------------------------------------------------

def genie_extract_preferences(chat_history: list) -> dict:
    """
    Genie reads the conversation history and extracts structured user preferences.
    Called before recipe generation to produce a clean preferences dict.

    Returns:
        dict with: ingredients, diet, allergies, likes, dislikes, summary
    """
    history_str = "\n".join(
        f"{msg['role'].title()}: {msg['content']}"
        for msg in chat_history
    )

    prompt = (
        "You are Genie, an expert AI chef. Read this conversation and extract "
        "the user's cooking preferences thoroughly.\n\n"
        f"Conversation:\n{history_str}\n\n"
        "Extract: diet restrictions, allergies, liked foods, disliked foods, "
        "specific ingredients mentioned, and any other preferences "
        "(cook time, cuisine type, equipment, spice level, servings, etc.).\n\n"
        "Return ONLY valid raw JSON:\n"
        "{\n"
        '  "ingredients": "comma separated ingredients the user mentioned, or empty string",\n'
        '  "diet": "e.g. Vegetarian, Vegan, Low-Carb, Gluten-Free, or empty string",\n'
        '  "allergies": ["allergy1", "allergy2"],\n'
        '  "likes": ["like1", "like2"],\n'
        '  "dislikes": ["dislike1", "dislike2"],\n'
        '  "summary": "Concise summary of all other prefs: cook time, cuisine, equipment, servings, spice level, etc."\n'
        "}"
    )

    try:
        res_text = call_api(prompt=prompt, json_mode=True)
        data = json.loads(res_text)
        return {
            "ingredients": data.get("ingredients", ""),
            "diet": data.get("diet", ""),
            "allergies": data.get("allergies", []),
            "likes": data.get("likes", []),
            "dislikes": data.get("dislikes", []),
            "summary": data.get("summary", "")
        }
    except Exception:
        return {
            "ingredients": "",
            "diet": "",
            "allergies": [],
            "likes": [],
            "dislikes": [],
            "summary": ""
        }


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _validate_and_normalize(data: dict) -> dict:
    """Ensure all required fields exist with sensible defaults."""
    return {
        "title": data.get("title", "Genie Special"),
        "display_title": data.get("display_title", "Genie's Special Dish 🍽️"),
        "servings": int(data.get("servings", 2)),
        "ingredients": [str(i).title() for i in data.get("ingredients", [])],
        "steps": data.get("steps", []),
        "tags": data.get("tags", ["AI-Generated"]),
        "note": data.get("note", "Ta-da! Cook with love and enjoy every bite! 🧞✨"),
        "safety_passed": bool(data.get("safety_passed", True)),
        "warnings": data.get("warnings", []),
        "nutrition": data.get("nutrition", {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}),
        "diet_tags": data.get("diet_tags", []),
        "substitutes": data.get("substitutes", {}),
        "upgrades": data.get("upgrades", []),
        "pairing": data.get("pairing", {
            "alcoholic": "Crisp white wine",
            "non_alcoholic": "Sparkling water with lemon"
        }),
        "sustainability": data.get("sustainability", {
            "co2_footprint": "1.3 kg CO2e",
            "water_footprint": "Medium",
            "grade": "C",
            "eco_tip": "Buy local, seasonal ingredients to reduce transport footprint."
        }),
    }
