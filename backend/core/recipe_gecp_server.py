import time
from concurrent.futures import ThreadPoolExecutor
from utils.security import sanitize_text, validate_ingredient_list
from utils.mnt_parser import parse_ingredients
from core.narrator import narrate_recipe
from agents.chef_agent import create_recipe
from agents.nutritionist_agent import analyze_nutrition
from agents.pantry_agent import suggest_substitutes
from agents.sommelier_agent import suggest_pairing
from agents.verifier_agent import verify_ingredients
from agents.sustainability_agent import analyze_sustainability

# Utilities
from utils.cache_manager import get_cached_recipe, set_cached_recipe
from utils.logger import log_performance, log_error

# Resilient local fallback generators
def fallback_nutrition(ingredients: list[str]) -> dict:
    cnt = len(ingredients)
    return {
        "totals": {
            "calories": cnt * 85,
            "protein": cnt * 4,
            "carbs": cnt * 10,
            "fat": cnt * 3
        },
        "tags": ["Nutritious", "Balanced"]
    }

def fallback_pantry() -> dict:
    return {
        "substitutes": {
            "Butter": ["Olive Oil", "Coconut Oil"],
            "Milk": ["Almond Milk", "Oat Milk"],
            "Wheat Flour": ["Gluten-Free Flour Blend"]
        },
        "upgrades": ["Garnish with fresh parsley or cilantro", "Top with toasted sesame seeds"]
    }

def fallback_pairing() -> dict:
    return {
        "pairing": "Crisp sparkling water with lemon or a light Pinot Grigio.",
        "reason": "Accents fresh, home-cooked flavours perfectly."
    }

def fallback_sustainability() -> dict:
    return {
        "co2_footprint": "1.3 kg CO2e",
        "water_footprint": "Medium",
        "grade": "C",
        "eco_tip": "Incorporate local greens and seasonal vegetables to minimize transport footprint."
    }


def process_input(raw_text: str, preferences: dict = None) -> dict:
    """Process raw text, apply agentic pipeline with parallel executor, caching, logging, and fallbacks."""
    start_time = time.time()
    if preferences is None:
        preferences = {}
        
    # Check Database Cache first
    cached = get_cached_recipe(raw_text, preferences)
    if cached:
        duration = time.time() - start_time
        log_performance("process_input (CACHE HIT)", duration, f"Ingredients: {raw_text[:40]}")
        return cached

    # 1. Sanitize text
    sanitized_input = sanitize_text(raw_text)
    
    # 2. Parse raw ingredients
    raw_ingredients = parse_ingredients(sanitized_input)
    
    # 3. Verify ingredients (Allergies & Diets filtering)
    filtered_ingredients, verifier_warnings = verify_ingredients(raw_ingredients, preferences)
    
    # 4. Validate ingredient list
    is_valid, error_message = validate_ingredient_list(filtered_ingredients)
    if not is_valid:
        log_error("process_input validation", error_message)
        raise ValueError(error_message)
        
    # 5. Generate base recipe using Chef Agent (Genie) with Self-Correction Loop
    pref_context = preferences.get("summary", "")
    feedback_msg = ""
    recipe_data = {}
    all_warnings = list(verifier_warnings)
    
    for attempt in range(3):
        try:
            recipe_data = create_recipe(filtered_ingredients, preferences_context=pref_context + feedback_msg)
            # Verify generated recipe ingredients for safety compliance
            _, recipe_warnings = verify_ingredients(recipe_data["ingredients"], preferences)
            if not recipe_warnings:
                break
            feedback_msg = f"\n[CORRECTION ATTEMPT {attempt+1}]: Your previous recipe suggestion contained ingredients violating safety rules: {', '.join(recipe_warnings)}. Please adjust the recipe title, ingredients, and instructions to exclude them."
            all_warnings.extend(recipe_warnings)
        except Exception as chef_err:
            log_error("Chef Agent generation", str(chef_err))
            # If chef fails, raise or fallback
            if attempt == 2:
                raise chef_err

    # Ensure display details are parsed
    try:
        narrated = narrate_recipe(recipe_data)
    except Exception as narr_err:
        log_error("Narrator Agent", str(narr_err))
        narrated = {
            "display_title": recipe_data.get("title", "Genie Dish"),
            "steps": recipe_data.get("steps", []),
            "note": "Enjoy this custom chef-created dish!"
        }

    # 6. Execute secondary agents concurrently using ThreadPoolExecutor for latency minimization
    nutrition_res = None
    pantry_res = None
    pairing_res = None
    sustainability_res = None

    with ThreadPoolExecutor(max_workers=1) as executor:
        # Submit tasks
        future_nut = executor.submit(analyze_nutrition, recipe_data.get("title", "Genie Dish"), filtered_ingredients)
        future_pan = executor.submit(suggest_substitutes, recipe_data.get("title", "Genie Dish"), filtered_ingredients)
        future_pair = executor.submit(suggest_pairing, recipe_data.get("title", "Genie Dish"), recipe_data.get("tags", []))
        future_sus = executor.submit(analyze_sustainability, recipe_data.get("title", "Genie Dish"), filtered_ingredients)

        # Retrieve with resilient local fallbacks in case of API exception
        try:
            nutrition_res = future_nut.result(timeout=10)
        except Exception as ex:
            log_error("Concurrent Nutrition Agent", str(ex))
            nutrition_res = fallback_nutrition(filtered_ingredients)

        try:
            pantry_res = future_pan.result(timeout=10)
        except Exception as ex:
            log_error("Concurrent Pantry Agent", str(ex))
            pantry_res = fallback_pantry()

        try:
            pairing_res = future_pair.result(timeout=10)
        except Exception as ex:
            log_error("Concurrent Sommelier Agent", str(ex))
            pairing_res = fallback_pairing()

        try:
            sustainability_res = future_sus.result(timeout=10)
        except Exception as ex:
            log_error("Concurrent Sustainability Agent", str(ex))
            sustainability_res = fallback_sustainability()

    # Compile result object
    result = {
        "display_title": narrated["display_title"],
        "ingredients": recipe_data.get("ingredients", []),
        "steps": narrated["steps"],
        "servings": recipe_data.get("servings", 2),
        "tags": recipe_data.get("tags", []),
        "note": narrated["note"],
        "nutrition": nutrition_res.get("totals", {}),
        "diet_tags": nutrition_res.get("tags", []),
        "substitutes": pantry_res.get("substitutes", {}),
        "upgrades": pantry_res.get("upgrades", []),
        "pairing": pairing_res,
        "sustainability": sustainability_res,
        "warnings": list(set(all_warnings))
    }

    # Save to SQLite Cache for future fast hits
    try:
        set_cached_recipe(raw_text, preferences, result)
    except Exception as cache_err:
        log_error("Cache Save", str(cache_err))

    duration = time.time() - start_time
    log_performance("process_input (CACHE MISS)", duration, f"Ingredients: {raw_text[:40]}")
    
    return result
