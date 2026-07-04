import re

def is_allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension (.txt or .json)."""
    return filename.lower().endswith(('.txt', '.json'))

def sanitize_text(text: str) -> str:
    """Remove HTML/script-like tags and trim whitespace."""
    if not text:
        return ""
    # Simple regex to strip HTML/script tag structures
    cleaned = re.sub(r'<[^>]*>', '', text)
    return cleaned.strip()

def validate_ingredient_list(items: list[str]) -> tuple[bool, str]:
    """Validate that the ingredient list satisfies all requirements."""
    if not items or len(items) == 0:
        return False, "Please provide at least 1 ingredient."
    if len(items) > 30:
        return False, "Too many ingredients! Please provide at most 30 items."
    for i, item in enumerate(items):
        if not isinstance(item, str) or not item.strip():
            return False, f"Ingredient at position {i+1} is empty or invalid."
    return True, ""
