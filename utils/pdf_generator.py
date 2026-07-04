# utils/pdf_generator.py
import io

def generate_recipe_card(recipe: dict) -> bytes:
    """Generate a printable text recipe card in bytes."""
    title = recipe.get("display_title", "Recipe").upper()
    servings = recipe.get("servings", 2)
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])
    note = recipe.get("note", "")
    
    nut = recipe.get("nutrition", {})
    co2 = recipe.get("sustainability", {}).get("co2_footprint", "N/A")
    grade = recipe.get("sustainability", {}).get("grade", "N/A")
    eco_tip = recipe.get("sustainability", {}).get("eco_tip", "")
    
    pairing = recipe.get("pairing", {})
    if isinstance(pairing, dict):
        pairing_text = pairing.get("pairing", "N/A")
    else:
        pairing_text = str(pairing)
        
    card = []
    card.append("=" * 60)
    card.append(f"               MEALGENIE CUSTOM RECIPE")
    card.append("=" * 60)
    card.append(f"RECIPE: {title}")
    card.append(f"SERVINGS: {servings}")
    card.append("-" * 60)
    
    card.append("INGREDIENTS:")
    for item in ingredients:
        card.append(f" - {item}")
    card.append("-" * 60)
    
    card.append("INSTRUCTIONS:")
    for idx, step in enumerate(steps, 1):
        card.append(f" {idx}. {step}")
    card.append("-" * 60)
    
    if note:
        card.append(f"CHEF'S NOTE: {note}")
        card.append("-" * 60)
        
    card.append("NUTRITIONAL INFORMATION:")
    card.append(f" - Calories: {nut.get('calories', 0)} kcal")
    card.append(f" - Protein: {nut.get('protein', 0)}g")
    card.append(f" - Carbs: {nut.get('carbs', 0)}g")
    card.append(f" - Fat: {nut.get('fat', 0)}g")
    card.append("-" * 60)
    
    card.append("SUSTAINABILITY SCORE:")
    card.append(f" - Eco-Grade: {grade}")
    card.append(f" - Carbon Footprint: {co2}")
    if eco_tip:
        card.append(f" - Eco-Tip: {eco_tip}")
    card.append("-" * 60)
    
    card.append(f"SOMMELIER PAIRING: {pairing_text}")
    card.append("=" * 60)
    card.append("            Thank you for cooking with MealGenie!")
    card.append("=" * 60)
    
    return "\n".join(card).encode("utf-8")
