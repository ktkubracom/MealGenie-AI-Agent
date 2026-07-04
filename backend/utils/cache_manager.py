# utils/cache_manager.py
import sqlite3
import hashlib
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "recipe_cache.db")

def init_db():
    """Initialize the SQLite database cache table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recipe_cache (
            cache_key TEXT PRIMARY KEY,
            recipe_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def _generate_key(ingredients: str, preferences: dict) -> str:
    """Generate a stable MD5 hash based on inputs."""
    # Clean ingredients and sort keys of preferences for consistency
    clean_ingredients = ingredients.strip().lower()
    pref_str = json.dumps(preferences, sort_keys=True).lower()
    raw_key = f"{clean_ingredients}||{pref_str}"
    return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

def get_cached_recipe(ingredients: str, preferences: dict) -> dict:
    """Retrieve cached recipe if it exists, otherwise return None."""
    init_db()
    key = _generate_key(ingredients, preferences)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT recipe_json FROM recipe_cache WHERE cache_key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except Exception:
            return None
    return None

def set_cached_recipe(ingredients: str, preferences: dict, recipe: dict):
    """Save a generated recipe to the SQLite database cache."""
    init_db()
    key = _generate_key(ingredients, preferences)
    recipe_json = json.dumps(recipe)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO recipe_cache (cache_key, recipe_json)
        VALUES (?, ?)
    """, (key, recipe_json))
    conn.commit()
    conn.close()
