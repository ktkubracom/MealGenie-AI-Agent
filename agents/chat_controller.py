# agents/chat_controller.py
"""Utility to manage the dynamic pre-recipe conversational flow using Gemini.
It handles state initialization, dynamic conversational responses, and preference extraction.
"""

import random
import json
import streamlit as st
from .api_client import call_api

# Keys to maintain state
_STATE_KEYS = [
    "chat_history",         # list of {"role": str, "content": str}
    "num_questions_asked",  # int
    "target_questions",     # int (random between 3 and 7)
    "chat_complete",        # bool
    "active_ingredients",   # str representation of ingredients checked
]

def initialize_chat():
    """Initialize state for a new conversational session."""
    if "target_questions" not in st.session_state:
        st.session_state.target_questions = random.randint(3, 7)
    if "num_questions_asked" not in st.session_state:
        st.session_state.num_questions_asked = 0
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chat_complete" not in st.session_state:
        st.session_state.chat_complete = False
    if "active_ingredients" not in st.session_state:
        st.session_state.active_ingredients = ""

def reset_chat_flow():
    """Reset the chat controller states."""
    for key in _STATE_KEYS:
        if key in st.session_state:
            del st.session_state[key]
    initialize_chat()

def get_agent_response(ingredients: str) -> str:
    """Generate the agent's next conversational reply using Gemini."""
    initialize_chat()
    
    from utils.memory_manager import load_user_profile
    user_uid = st.session_state.get('user_uid', '')
    profile = load_user_profile(user_uid)
    profile_ctx = f"User Profile (Memory) -> Allergies: {', '.join(profile.get('allergies', []))}, Diet: {profile.get('diet', '')}, Likes: {', '.join(profile.get('likes', []))}, Dislikes: {', '.join(profile.get('dislikes', []))}."

    ing_text = f"using: {ingredients}" if ingredients and ingredients != "surprise me" else "with whatever ingredients they have"
        
    system_instruction = (
        f"You are Genie, a friendly, expert AI kitchen chef. The user wants to make a recipe {ing_text}.\n"
        f"{profile_ctx}\n"
        f"Converse with them naturally to gather details. If they haven't mentioned any ingredients yet, ask them what they have in their fridge or pantry! Otherwise, ask about allergies, diet, cook time, cuisine, equipment, etc.\n"
        f"Rules:\n"
        f"1. Acknowledge and reply directly to the user's latest response.\n"
        f"2. Ask exactly ONE relevant question at a time (e.g., about allergies, diet, or time).\n"
        f"3. Do not repeat questions or topics already asked.\n"
        f"4. CRITICAL: Avoid interrogating the user. Limit yourself to a maximum of 5 or 7 questions total across the conversation.\n"
        f"5. Once you have basic ingredients and 1-2 preferences, STOP asking questions and enthusiastically suggest they click the 'Generate Custom Recipe' button on the sidebar so you can start cooking! but dont pressure them like it should be free they can ask changes and more and it all should be conversational, Genie-Human sounded and Engaging for the user"
    )
    
    try:
        response = call_api(json_mode=False, system_instruction=system_instruction, messages=st.session_state.chat_history[-15:])
        return response.strip()
    except Exception as e:
        return f"Oops, my magic is fizzling! An error occurred: {e}"

def extract_preferences() -> dict:
    """Extract diet, allergies, ingredients, and general preferences from the conversation history using Gemini."""
    initialize_chat()
    history_str = ""
    for msg in st.session_state.chat_history:
        history_str += f"{msg['role'].title()}: {msg['content']}\n"
        
    prompt = (
        f"Analyze the following conversation between the user and Genie the chef:\n{history_str}\n"
        f"Extract the dietary restrictions (e.g. Vegetarian, Vegan, Low-Carb, Gluten-Free), allergies "
        f"(e.g. peanut, dairy, soy), likes, dislikes, and the specific ingredients they want to use. "
        f"Return the result ONLY as a JSON object matching this schema:\n"
        "{\n"
        '  "ingredients": "comma separated string of ingredients the user has, or empty string",\n'
        '  "diet": "extracted diet or empty string",\n'
        '  "allergies": ["allergy1", "allergy2"],\n'
        '  "likes": ["like1", "like2"],\n'
        '  "dislikes": ["dislike1", "dislike2"],\n'
        '  "summary": "a summary of other preferences like cook time, equipment, cuisine, servings"\n'
        "}\n"
        "Return ONLY valid raw JSON."
    )
    try:
        res_text = call_api(prompt=prompt, json_mode=True)
        data = json.loads(res_text)
        
        from utils.memory_manager import update_user_profile
        user_uid = st.session_state.get('user_uid', '')
        updated_profile = update_user_profile(user_uid, data)
        
        # Merge the persistent profile into the returned data
        data["allergies"] = updated_profile.get("allergies", [])
        data["diet"] = updated_profile.get("diet", "")
        data["likes"] = updated_profile.get("likes", [])
        data["dislikes"] = updated_profile.get("dislikes", [])
        
        return {
            "ingredients": data.get("ingredients", ""),
            "diet": data.get("diet", ""),
            "allergies": data.get("allergies", []),
            "likes": data.get("likes", []),
            "dislikes": data.get("dislikes", []),
            "summary": data.get("summary", "")
        }
    except Exception:
        return {"diet": "", "allergies": [], "likes": [], "dislikes": [], "summary": ""}
