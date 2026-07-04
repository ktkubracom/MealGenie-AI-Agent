import re

def parse_ingredients(raw_text: str) -> list[str]:
    """Split ingredients by commas and newlines, clean, normalize, and de-duplicate while maintaining order."""
    if not raw_text:
        return []
    
    # Split by comma or newline
    items = re.split(r'[,\n]', raw_text)
    
    parsed = []
    seen = set()
    
    for item in items:
        cleaned = item.strip().lower()
        if not cleaned:
            continue
        
        # Normalize simple plurals
        if cleaned == "tomatoes":
            cleaned = "tomato"
        elif cleaned == "potatoes":
            cleaned = "potato"
        elif cleaned == "onions":
            cleaned = "onion"
        elif cleaned == "carrots":
            cleaned = "carrot"
            
        # De-duplicate while preserving original order
        if cleaned not in seen:
            seen.add(cleaned)
            parsed.append(cleaned)
            
    return parsed
