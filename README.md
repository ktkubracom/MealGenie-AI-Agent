# 🧞‍♂️ MealGenie: Your Personal AI Kitchen Swarm

<div align="center">
  <img src="assets/mealgenie_hero.png" alt="MealGenie Dashboard" />
</div>

## 🚨 The Problem
Every day, households waste a massive amount of food simply because people don't know what to cook with the ingredients they already have. Furthermore, maintaining dietary restrictions, tracking nutrition, and finding the time to plan meals can be incredibly overwhelming. There is a strong need for a "concierge" service that can streamline this daily chore, reducing food waste and simplifying our lives.

## ✨ The Solution
**MealGenie** is a cutting-edge, agentic AI web application designed for the **Kaggle Vibecoding Capstone Project (Concierge Track)**. It leverages a swarm of specialized AI agents to generate personalized, sustainable recipes based on what is currently in your fridge.

By simply uploading an image of your ingredients (Pantry Vision), the agents work together to:
1. Identify your ingredients and suggest optimal uses.
2. Formulate a base recipe (Head Chef).
3. Ensure it meets your dietary needs and calculate macros (Nutritionist).
4. Pair it with the perfect beverage (Sommelier).
5. Compile it into a beautiful, exportable PDF recipe card.

## 🧩 Architecture

MealGenie is built using **Streamlit** for a fluid, highly interactive frontend, and orchestrates a swarm of **Gemini**-powered AI agents in the backend.

```mermaid
graph TD
    User(["User: Ingredients & Preferences"]) -->|Chat & Image Upload| Streamlit["Streamlit UI (app.py)"]
    Streamlit -->|Retrieves/Saves Profile| Firebase["Firebase Firestore (Memory)"]
    Streamlit -->|Delegates Task| Coordinator["Genie Orchestrator Agent"]
    Coordinator -->|Analyzes Image| Vision["Pantry Vision API"]
    Coordinator -->|Assigns Task| Chef["Head Chef Agent"]
    Chef -->|Drafts Recipe| Nutritionist["Nutritionist Agent"]
    Nutritionist -->|Adds Macros| Sommelier["Sommelier Agent"]
    Sommelier -->|Finalizes| Streamlit
    Streamlit -->|Renders| UI["Interactive Recipe Profile & PDF Export"]
```

### Key Components:
- **Frontend**: Streamlit (`app.py`) providing a modern glassmorphic interface.
- **AI Agents**: Specialized Python modules under `backend/agents/` that handle scoped tasks.
- **Memory**: Firebase Firestore is used for persistent memory, allowing the app to remember allergies, likes, and dislikes across sessions (accessed via a default guest profile for seamless demoing).
- **Core Engine**: Gemini AI models driving the agent reasoning.

---

## 🚀 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/ktkubracom/MealGenie-AI-Agent.git
cd MealGenie-AI-Agent
```

### 2. Environment Setup
Create and activate a Python virtual environment:
```bash
python -m venv venv
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Secrets
MealGenie uses Streamlit's secrets management for the API keys. Create a `.streamlit/secrets.toml` file in the root directory:
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your-gemini-api-key"

[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-xxx@your-project-id.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
```
*(Note: As we removed user login for the Kaggle evaluation, Firebase Auth is bypassed, but Firestore is still used for storing persistent user dietary profiles under a generic "guest" account.)*

### 5. Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```
The application will open in your default browser at `http://localhost:8501`.

---

## 🛡️ Security Note
The `.streamlit/secrets.toml` file is excluded via `.gitignore`. Never commit secret keys or credentials to the repository. The application uses input validation to ensure uploaded images are secure before passing them to the Vision API.
