def narrate_recipe(recipe: dict) -> dict:
    """Convert recipe into a fun narrated format with emojis and a cheerful note."""
    title = recipe.get("title", "Genie Special")
    tags = recipe.get("tags", [])
    
    # Choose emoji based on tags
    emoji = "🍽️"
    if "Pasta" in tags:
        emoji = "🍝"
    elif "Rice Bowl" in tags:
        emoji = "🍛"
    elif "Salad" in tags:
        emoji = "🥗"
    elif "Skillet" in tags:
        emoji = "🍳"
        
    display_title = f"Genie’s Special {title} {emoji}"
    
    # Add emojis to steps
    step_emojis = ["🔪", "🍳", "🧂", "✨"]
    narrated_steps = []
    for i, step in enumerate(recipe.get("steps", [])):
        prefix = step_emojis[i % len(step_emojis)]
        narrated_steps.append(f"{prefix} {step}")
        
    note = "Ta-da! Your delicious meal is ready. Cook with love and enjoy every bite! 🧞✨"
    
    return {
        "display_title": display_title,
        "ingredients": recipe.get("ingredients", []),
        "steps": narrated_steps,
        "servings": recipe.get("servings", 2),
        "tags": tags,
        "note": note
    }

