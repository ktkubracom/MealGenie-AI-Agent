import streamlit as st
import json
import os
import sys

# Ensure backend directory is in sys.path so we can import from agents, core, utils
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from utils.security import is_allowed_file
from core.recipe_gecp_server import process_input
from agents.chat_controller import initialize_chat, reset_chat_flow, get_agent_response, extract_preferences
from agents.genie_agent import genie_chat
from agents.image_agent import generate_recipe_image
from utils.pdf_generator import generate_recipe_card

# Page configuration
st.set_page_config(page_title="MealGenie", page_icon="🧞", layout="wide")

if "user_uid" not in st.session_state:
    import uuid
    st.session_state.user_uid = f"guest_{uuid.uuid4().hex[:8]}"
if "user_email" not in st.session_state:
    st.session_state.user_email = f"{st.session_state.user_uid}@mealgenie.local"

# Custom CSS for modern, premium look, float animations, and cards
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Main page layout adjustments */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    font-family: 'Outfit', sans-serif;
    background-color: #0B0F19; /* Deeper slate/charcoal */
    color: #f8fafc;
}
/* Ensure proper padding for fluid layout */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Title text color styling */
.title-container {
    text-align: left;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.title-container h1 {
    font-size: 3.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FF6B6B, #FCA048); /* Coral to Gold */
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
}
.subtitle {
    color: #64748B; /* Muted slate */
    font-size: 1.2rem;
    text-align: left;
    margin-bottom: 25px;
    font-weight: 400;
}

/* Custom premium components */
.card {
    background: rgba(15, 23, 42, 0.5); /* Semi-transparent */
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
    margin-bottom: 20px;
}

/* Tab System Styling (Pill-shaped/Segmented) */
[data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(15, 23, 42, 0.4);
    padding: 6px;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
[data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px;
    padding: 8px 16px;
    border: none !important;
    color: #94A3B8 !important;
}
[data-baseweb="tab"]:focus {
    outline: none !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    background: rgba(255, 255, 255, 0.1);
    color: #f8fafc !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
/* Hide the default animated underline bar */
[data-baseweb="tab-highlight"] {
    display: none;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #FF6B6B, #FCA048) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
}
button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #cbd5e1 !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
}
button[kind="secondary"]:hover {
    border-color: rgba(255, 255, 255, 0.4) !important;
    color: white !important;
}

/* Chat Input Styling */
[data-testid="stChatInput"] {
    background: rgba(15, 23, 42, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 24px !important;
}
[data-testid="stChatInput"] textarea {
    color: white !important;
}

/* Chat Bubbles Styling */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1.5rem !important;
    margin-bottom: 12px;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(255, 255, 255, 0.05);
}
[data-testid="chatAvatarIcon-user"] {
    background-color: #64748B !important;
}
/* Genie AI Messages */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(255, 107, 107, 0.03);
    border: 1px solid rgba(255, 107, 107, 0.1);
}

/* Banners (Warning/Info) */
[data-testid="stAlert"] {
    background: rgba(15, 23, 42, 0.4) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-left: 4px solid #3b82f6 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
[data-testid="stAlert"]:has(svg[data-icon="triangle-exclamation"]) {
    border-left: 4px solid #f59e0b !important;
}
[data-testid="stAlert"]:has(svg[data-icon="x-circle"]) {
    border-left: 4px solid #ef4444 !important;
}

.recipe-title {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FF6B6B, #FCA048);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.servings-tag {
    display: inline-block;
    background: rgba(255, 107, 107, 0.1);
    border: 1px solid rgba(255, 107, 107, 0.3);
    color: #FF6B6B;
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.95rem;
    margin-bottom: 20px;
    font-weight: 600;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-top: 25px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 6px;
}

.ingredient-chip {
    display: inline-block;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 6px 14px;
    margin: 4px 6px 4px 0;
    font-size: 0.95rem;
    transition: all 0.2s ease;
}
.ingredient-chip:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
}

.step-item {
    margin-bottom: 16px;
    line-height: 1.6;
    font-size: 1.05rem;
}

.cheerful-note {
    font-style: italic;
    color: #cbd5e1;
    background: rgba(255, 107, 107, 0.05);
    border-left: 4px solid #FF6B6B;
    padding: 15px 20px;
    border-radius: 8px;
    margin-top: 25px;
    font-size: 1rem;
}

/* Nutrition Hub Styling */
.nutrition-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin-bottom: 20px;
}
.nutrition-card {
    background: rgba(15, 23, 42, 0.6);
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.nutrition-value {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 5px;
}
.nutrition-label {
    font-size: 0.85rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.diet-badge {
    display: inline-block;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    margin-right: 8px;
    margin-top: 8px;
    font-weight: 500;
}

/* Pantry & Wine styling */
.swap-card {
    background: rgba(15, 23, 42, 0.4);
    border-left: 4px solid #FCA048;
    border-radius: 6px;
    padding: 12px 18px;
    margin-bottom: 12px;
}
.wine-card {
    background: rgba(255, 107, 107, 0.05);
    border-left: 4px solid #FF6B6B;
    border-radius: 6px;
    padding: 15px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# 1. Floating SVG Icons effect at the top
st.markdown("""

""", unsafe_allow_html=True)

# Initialize Session States
if "recipe" not in st.session_state:
    st.session_state.recipe = None

# Initialize Chat State via controller
initialize_chat()

# Two column layout: Left (Ingredients/Recipe details & Tabs), Right (Genie Chat Agent)
col_main, col_chat = st.columns([1.6, 1])

# Determine active ingredients input
file_ingredients = ""

with col_main:
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        # App Title Header
        st.markdown("""
        <div class="title-container">
            <h1>MealGenie - AI Agent</h1>
        </div>
        <div class="subtitle">Your multi-agent AI kitchen assistant.</div>
        """, unsafe_allow_html=True)
    with col_logout:
        pass # Placeholder to preserve layout

    # Establish Permanent Tabs on the Left Side
    tab_recipe, tab_nutrition, tab_pantry, tab_sommelier = st.tabs([
        "Recipe Instructions",
        "Nutrition Hub",
        "Pantry Swap",
        "Sommelier"
    ])

    # Start chat automatically if empty
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "Hello there! I'm Genie, your friendly kitchen chef. To get started, what ingredients do you have in your kitchen today?"
        })
        st.session_state.num_questions_asked = 1

    # Show Consultation Progress & Generate Button
    if not st.session_state.recipe:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Consultation & Recipe Profile")

        col_btns = st.columns(2)
        with col_btns[0]:
            generate_click = st.button("Generate Custom Recipe", type="primary", use_container_width=True)
        with col_btns[1]:
            reset_click = st.button("Reset Consultation", type="secondary", use_container_width=True)

        if reset_click:
            reset_chat_flow()
            st.rerun()

        if generate_click:
            with st.spinner("Genie and the agents are collaborating..."):
                try:
                    prefs_extracted = extract_preferences()
                    # User's ingredients are now extracted by Gemini
                    ingredients_text = prefs_extracted.get("ingredients", "surprise me")
                    if not ingredients_text.strip():
                        ingredients_text = "surprise me"
                        
                    recipe = process_input(ingredients_text, prefs_extracted)
                    recipe["image_url"] = generate_recipe_image(recipe["display_title"], recipe["ingredients"])
                    st.session_state.recipe = recipe
                    st.session_state.active_ingredients = ingredients_text
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"I have conjured up a custom **{recipe['display_title']}** recipe for you! You can view the details in the other tabs on the left, and ask me any follow-up questions here."
                    })
                    st.balloons()
                    st.rerun()
                except ValueError as ve:
                    st.error(f"⚠️ Warning: {ve}")
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Populate Recipe Card Tab
    with tab_recipe:
        if st.session_state.recipe:
            recipe = st.session_state.recipe
            if recipe.get("warnings"):
                for warning in recipe["warnings"]:
                    st.warning(f"Verifier Agent: {warning}")

            st.markdown(f"<div class='recipe-title'>{recipe['display_title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='servings-tag'>Servings: {recipe['servings']}</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            if recipe.get("image_url"):
                st.image(recipe["image_url"], use_container_width=True)
            
            st.markdown("<div class='section-title'>Ingredients Needed</div>", unsafe_allow_html=True)
            st.markdown("<div>" + "".join(f'<span class="ingredient-chip">{item}</span>' for item in recipe['ingredients']) + "</div>", unsafe_allow_html=True)
            
            st.markdown("<div class='section-title'>Instructions</div>", unsafe_allow_html=True)
            for idx, step in enumerate(recipe['steps'], 1):
                st.markdown(f"<div class='step-item'><strong>Step {idx}:</strong> {step}</div>", unsafe_allow_html=True)

            if recipe.get("note"):
                st.markdown(f"<div class='cheerful-note'><strong>Chef's Note:</strong> {recipe['note']}</div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            recipe_data_bytes = generate_recipe_card(recipe)
            st.download_button(
                label="Export Recipe Card",
                data=recipe_data_bytes,
                file_name=f"{recipe['display_title'].replace(' ', '_')}_Recipe.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Your recipe instructions will appear here once generated. Complete the consultation and click Generate!")

    # Populate Nutrition Hub Tab
    with tab_nutrition:
        if st.session_state.recipe:
            recipe = st.session_state.recipe
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Macronutrients Analysis</h3>", unsafe_allow_html=True)
            nut = recipe.get("nutrition", {"calories": 0, "protein": 0, "carbs": 0, "fat": 0})
            
            st.markdown(f"""
            <div class="nutrition-grid">
                <div class="nutrition-card" style="border-top: 4px solid #f472b6;">
                    <div class="nutrition-value" style="color: #f472b6;">{nut.get('calories')}</div>
                    <div class="nutrition-label">Calories (kcal)</div>
                </div>
                <div class="nutrition-card" style="border-top: 4px solid #3b82f6;">
                    <div class="nutrition-value" style="color: #3b82f6;">{nut.get('protein')}g</div>
                    <div class="nutrition-label">Protein</div>
                </div>
                <div class="nutrition-card" style="border-top: 4px solid #f59e0b;">
                    <div class="nutrition-value" style="color: #f59e0b;">{nut.get('carbs')}g</div>
                    <div class="nutrition-label">Carbs</div>
                </div>
                <div class="nutrition-card" style="border-top: 4px solid #10b981;">
                    <div class="nutrition-value" style="color: #10b981;">{nut.get('fat')}g</div>
                    <div class="nutrition-label">Fat</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Labels/badges
            st.markdown("<h4>Dietary Badges Detected</h4>", unsafe_allow_html=True)
            dtags = recipe.get("diet_tags", [])
            if dtags:
                st.markdown("<div>" + "".join(f'<span class="diet-badge">{t}</span>' for t in dtags) + "</div>", unsafe_allow_html=True)
            else:
                st.write("No specific dietary badges flagged.")
                
            # Sustainability Eco-Score Section
            st.markdown("<div class='section-title'>Sustainability & Eco-Score</div>", unsafe_allow_html=True)
            sus = recipe.get("sustainability", {})
            grade = sus.get("grade", "C")
            co2 = sus.get("co2_footprint", "N/A")
            eco_tip = sus.get("eco_tip", "")
            
            grade_colors = {
                "A": "#10b981", "B": "#34d399", "C": "#f59e0b",
                "D": "#f97316", "E": "#ef4444", "F": "#b91c1c"
            }
            g_color = grade_colors.get(grade, "#94a3b8")
            
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); border-left: 4px solid {g_color}; padding: 15px; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-weight: 600; font-size: 1.15rem;">Environmental Impact Grade</span>
                    <span style="background: {g_color}; color: #000; font-weight: 700; padding: 4px 14px; border-radius: 20px; font-size: 1.3rem;">Grade {grade}</span>
                </div>
                <p><strong>CO2 Footprint:</strong> {co2}</p>
                {"<p>🌱 <em>" + eco_tip + "</em></p>" if eco_tip else ""}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nutrition data will appear here once the recipe is generated.")

    # Populate Pantry swaps Tab
    with tab_pantry:
        if st.session_state.recipe:
            recipe = st.session_state.recipe
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Smart Swaps & Ingredient Upgrades</h3>", unsafe_allow_html=True)
            
            subs = recipe.get("substitutes", {})
            upgrades = recipe.get("upgrades", [])
            
            if subs:
                st.markdown("<h4>Alternatives & Substitutes</h4>", unsafe_allow_html=True)
                for ingredient, sub_list in subs.items():
                    sub_text = ", ".join(sub_list) if isinstance(sub_list, list) else str(sub_list)
                    st.markdown(f"<div class='swap-card'><strong>{ingredient}</strong>: Try replacing with <em>{sub_text}</em></div>", unsafe_allow_html=True)
            else:
                st.write("No substitutes needed.")

            if upgrades:
                st.markdown("<h4>Gourmet Upgrades</h4>", unsafe_allow_html=True)
                for upg in upgrades:
                    st.markdown(f"<div class='swap-card' style='border-left-color: #10b981;'>✨ {upg}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Swaps and pantry upgrade suggestions will appear here once the recipe is generated.")

    # Populate Sommelier Pairing Tab
    with tab_sommelier:
        if st.session_state.recipe:
            recipe = st.session_state.recipe
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3>Wine & Drink Pairings</h3>", unsafe_allow_html=True)
            pairing = recipe.get("pairing", {})
            if isinstance(pairing, dict):
                pairing_text = pairing.get("pairing", "A fresh sparkling water or light tea matches beautifully.")
                reason = pairing.get("reason", "")
            else:
                pairing_text = str(pairing)
                reason = ""
            
            st.markdown(f"""
            <div class="wine-card">
                <h4>🍷 Recommendation</h4>
                <p><strong>{pairing_text}</strong></p>
                {"<p><em>" + reason + "</em></p>" if reason else ""}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Drink and wine pairings will appear here once the recipe is generated.")

    # Dynamic Reset Button at bottom of column
    if st.session_state.recipe:
        if st.button("Conjure a New Recipe", use_container_width=True):
            st.session_state.recipe = None
            reset_chat_flow()
            st.session_state.active_ingredients = ""
            st.rerun()

with col_chat:
    st.subheader("Chat with Genie!")
    
    # Custom styling for chat area container
    st.markdown("""
    <style>
    .chat-container {
        border-radius: 12px;
        background: rgba(30, 41, 59, 0.4);
        padding: 15px;
        margin-bottom: 10px;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    /* Memory Pills */
    .memory-tracker-container {
        border-radius: 12px;
        background: rgba(30, 41, 59, 0.4);
        padding: 15px;
        margin-top: 10px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .memory-tracker-title {
        font-size: 0.9rem;
        color: #94A3B8;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .pill.allergy { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); }
    .pill.like { background: rgba(34, 197, 94, 0.2); color: #86efac; border: 1px solid rgba(34, 197, 94, 0.3); }
    .pill.dislike { background: rgba(249, 115, 22, 0.2); color: #fdba74; border: 1px solid rgba(249, 115, 22, 0.3); }
    .pill.diet { background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }
    
    .stChatInputContainer {
    </style>
    """, unsafe_allow_html=True)

    # Render conversational logs inside a scrollable container
    with st.container(height=600):
        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.write(chat["content"])

    # Memory Tracker Card
    from utils.memory_manager import load_user_profile
    user_prof = load_user_profile(st.session_state.get("user_uid", ""))
    
    st.markdown("<div class='memory-tracker-container'>", unsafe_allow_html=True)
    st.markdown("<div class='memory-tracker-title'>🧠 Genie Memory Tracker</div>", unsafe_allow_html=True)
    
    pills_html = ""
    if user_prof.get("diet"):
        pills_html += f"<span class='pill diet'>Diet: {user_prof['diet']}</span>"
    for al in user_prof.get("allergies", []):
        pills_html += f"<span class='pill allergy'>🚫 {al}</span>"
    for lk in user_prof.get("likes", []):
        pills_html += f"<span class='pill like'>❤️ {lk}</span>"
    for dl in user_prof.get("dislikes", []):
        pills_html += f"<span class='pill dislike'>👎 {dl}</span>"
        
    if pills_html:
        st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.8rem; color:#64748B;'>The Genie is listening... tell it your preferences!</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Chat input box
    user_msg = st.chat_input("Answer Genie or Ask follow-ups...")
    
    if user_msg:
        # Display user message immediately
        with st.chat_message("user"):
            st.write(user_msg)
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        
        # If we are in the questionnaire flow
        if not st.session_state.recipe:
            # Generate and ask the next question
            with st.spinner("Genie is listening..."):
                q = get_agent_response(st.session_state.active_ingredients)
                st.session_state.chat_history.append({"role": "assistant", "content": q})
            st.rerun()
        else:
            # Post-recipe follow-up chat
            with st.spinner("Genie is thinking..."):
                # Detect recipe modification intent via keyword matching (zero API calls)
                MOD_KEYWORDS = [
                    "change", "modify", "swap", "replace", "make it", "without",
                    "add ", "remove", "vegan", "spicy", "less", "more", "instead",
                    "adjust", "update", "redo", "different", "substitute", "switch",
                    "serving", "portion", "gluten", "dairy", "low carb", "keto"
                ]
                user_lower = user_msg.lower()
                is_mod = any(kw in user_lower for kw in MOD_KEYWORDS)

                if is_mod:
                    # Genie regenerates the recipe with updated context — 1 API call
                    try:
                        with st.spinner("Genie is updating the recipe..."):
                            prefs_extracted = extract_preferences()
                            prefs_extracted["summary"] = (
                                prefs_extracted.get("summary", "") +
                                f"\nUser update request: {user_msg}"
                            )
                            recipe = process_input(st.session_state.active_ingredients, prefs_extracted)
                            recipe["image_url"] = generate_recipe_image(recipe["display_title"], recipe["ingredients"])
                            st.session_state.recipe = recipe
                            response_text = (
                                f'Done! I\'ve updated the recipe based on your request: "{user_msg}". '
                                f"Check the recipe panels on the left — everything has been refreshed! 🧞✨"
                            )
                            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                    except Exception as e:
                        st.error(f"Failed to update recipe: {e}")
                else:
                    # Regular follow-up — Genie chats about the recipe (1 API call)
                    from utils.memory_manager import load_user_profile
                    user_uid = st.session_state.get("user_uid", "")
                    user_profile = load_user_profile(user_uid)
                    # Add recipe context to the last system message via ingredients
                    ingredients_str = ", ".join(st.session_state.recipe.get("ingredients", []))
                    try:
                        response_text = genie_chat(
                            ingredients=ingredients_str,
                            chat_history=st.session_state.chat_history[-10:],
                            user_profile=user_profile,
                        )
                        st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                    except Exception as e:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"Oops! I had a hiccup. ({e})"
                        })
                st.rerun()

# Force streamlit reload
