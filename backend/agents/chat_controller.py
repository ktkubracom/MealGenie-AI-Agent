# agents/chat_controller.py
"""
Manages the conversational pre-recipe flow.
All LLM logic is delegated to Genie (genie_agent.py).
This module only manages Streamlit session state.
"""

import random
import streamlit as st
from .genie_agent import genie_chat, genie_extract_preferences

# Session state keys
_STATE_KEYS = [
    "chat_history",
    "num_questions_asked",
    "target_questions",
    "chat_complete",
    "active_ingredients",
]


def initialize_chat():
    """Initialize state for a new conversational session."""
    if "target_questions" not in st.session_state:
        st.session_state.target_questions = random.randint(3, 5)
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
    """
    Ask Genie to respond to the user's latest message.
    Genie is a real LLM agent — he reads the full conversation history
    and decides what to say next based on context, not rules.
    """
    initialize_chat()

    from utils.memory_manager import load_user_profile
    user_uid = st.session_state.get("user_uid", "")
    user_profile = load_user_profile(user_uid)

    return genie_chat(
        ingredients=ingredients,
        chat_history=st.session_state.chat_history[-15:],
        user_profile=user_profile,
    )


def extract_preferences() -> dict:
    """
    Ask Genie to read the chat history and extract structured preferences.
    Genie uses the LLM to understand the conversation — not keyword matching.
    """
    initialize_chat()

    from utils.memory_manager import load_user_profile, update_user_profile
    user_uid = st.session_state.get("user_uid", "")

    # Genie reads the conversation and extracts prefs via LLM
    extracted = genie_extract_preferences(st.session_state.chat_history)

    # Persist to Firebase and merge with existing profile
    if user_uid:
        updated_profile = update_user_profile(user_uid, extracted)
        extracted["allergies"] = updated_profile.get("allergies", [])
        extracted["diet"] = updated_profile.get("diet", "")
        extracted["likes"] = updated_profile.get("likes", [])
        extracted["dislikes"] = updated_profile.get("dislikes", [])

    return extracted

