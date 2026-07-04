# utils/question_bank.py

"""A curated bank of pre‑recipe questions.
Each entry is a dict containing:
- ``id``: unique identifier (used to avoid repeats)
- ``text``: the question displayed to the user
- ``type``: ``radio`` or ``multiselect`` – determines the UI widget
- ``options``: list of possible answers (empty for free‑text)
- ``key``: session‑state key under which the answer will be stored
"""

QUESTION_BANK = [
    {
        "id": "diet_goal",
        "text": "What’s your primary diet goal for this meal?",
        "type": "radio",
        "options": ["Balanced", "Low‑Carb", "High‑Protein", "Low‑Fat", "Keto", "Vegetarian", "Vegan"],
        "key": "diet_goal",
    },
    {
        "id": "allergies",
        "text": "Do you have any allergies or foods you need to avoid?",
        "type": "multiselect",
        "options": ["Peanut", "Tree nut", "Soy", "Gluten", "Dairy", "Egg", "Shellfish", "Sesame", "Mustard"],
        "key": "allergies",
    },
    {
        "id": "cuisine",
        "text": "Which cuisine are you in the mood for?",
        "type": "radio",
        "options": ["Italian", "Mexican", "Indian", "Chinese", "Japanese", "Mediterranean", "Thai", "American"],
        "key": "cuisine",
    },
    {
        "id": "cook_time",
        "text": "How much time can you spend cooking?",
        "type": "radio",
        "options": ["≤ 15 min", "30 min", "45 min", "1 hour", "> 1 hour"],
        "key": "cook_time",
    },
    {
        "id": "equipment",
        "text": "What cooking equipment do you have?",
        "type": "multiselect",
        "options": ["Stovetop", "Oven", "Microwave", "Slow Cooker", "Air Fryer", "Instant Pot"],
        "key": "equipment",
    },
    {
        "id": "budget",
        "text": "What’s your budget range for this meal (USD)?",
        "type": "radio",
        "options": ["<$5", "$5‑$10", "$10‑$20", "$20‑$30", ">$30"],
        "key": "budget",
    },
    {
        "id": "servings",
        "text": "How many servings do you need?",
        "type": "radio",
        "options": ["1-2", "3-4", "5-6", "7-8", "More than 8"],
        "key": "servings",
    },
]
