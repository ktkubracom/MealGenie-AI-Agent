import os
import json
import urllib.request
import urllib.error

def _get_api_key() -> str:
    """Load Gemini API Key from environment or .env file."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
        
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        return line.strip().split("=", 1)[1].strip()
        except Exception:
            pass
            
    return ""

def _generate_recipe_ai(ingredients: list[str], api_key: str) -> dict:
    """Use Gemini 2.5 Flash to generate a recipe as Genie."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    prompt = (
        f"You are Genie, a professional AI chef. Create a single, creative, and delicious recipe using some or all of these ingredients: {', '.join(ingredients)}. "
        "You may assume basic kitchen staples (like salt, pepper, oil, water) are available. "
        "Return the response ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "title": "A fun, creative recipe title (without cooking emojis at the end)",\n'
        '  "servings": 2,\n'
        '  "ingredients": ["Ingredient 1", "Ingredient 2"],\n'
        '  "steps": [\n'
        '    "Step 1...",\n'
        '    "Step 2...",\n'
        '    "Step 3..."\n'
        '  ],\n'
        '  "tags": ["Tag1", "Tag2"]\n'
        "}\n"
        "Return ONLY valid raw JSON. Do not include markdown code block formatting like ```json or ```."
    )
    
    body = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    with urllib.request.urlopen(req, timeout=10) as response:
        res_data = response.read().decode("utf-8")
        res_json = json.loads(res_data)
        text_response = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Strip markdown wrappers if they exist
        if text_response.startswith("```"):
            lines = text_response.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text_response = "\n".join(lines).strip()
            
        parsed_recipe = json.loads(text_response)
        
        return {
            "title": parsed_recipe.get("title", "Genie Special"),
            "servings": int(parsed_recipe.get("servings", 2)),
            "ingredients": [item.title() for item in parsed_recipe.get("ingredients", [])],
            "steps": parsed_recipe.get("steps", []),
            "tags": parsed_recipe.get("tags", ["AI-Generated"])
        }

def generate_recipe(ingredients: list[str]) -> dict:
    """Generate a recipe based on ingredients using Gemini AI (Genie). Raises ValueError on failure."""
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("Quota full! Please try again later.")
    try:
        return _generate_recipe_ai(ingredients, api_key)
    except Exception as e:
        raise ValueError("Quota full! Please try again later.")


