import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# Hardcoded Web API Key provided by user for client-side Auth
WEB_API_KEY = "AIzaSyBOGf5xNdFu7IJYE51gl9hSZRJuA4ouS9s"

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(ROOT_DIR, "config", "firebase_credentials.json")

def init_firebase_admin():
    """Initialize Firebase Admin SDK for backend Firestore access."""
    if not firebase_admin._apps:
        cred = None
        
        # Try reading from Streamlit Secrets (for cloud deployment)
        try:
            import streamlit as st
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
        except Exception:
            pass
            
        # Fallback to local credentials JSON file
        if not cred:
            if not os.path.exists(CREDENTIALS_PATH):
                raise FileNotFoundError(f"Missing Firebase credentials file at: {CREDENTIALS_PATH}, and no 'firebase' secret found in st.secrets.")
            cred = credentials.Certificate(CREDENTIALS_PATH)
            
        firebase_admin.initialize_app(cred)

def get_db():
    """Get a connected Firestore client."""
    init_firebase_admin()
    return firestore.client()

def sign_up_with_email_and_password(email: str, password: str) -> dict:
    """Sign up a new user via Identity Toolkit API."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        error_data = resp.json()
        error_msg = error_data.get("error", {}).get("message", "Unknown error")
        raise ValueError(error_msg)

def sign_in_with_email_and_password(email: str, password: str) -> dict:
    """Sign in an existing user via Identity Toolkit API."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={WEB_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        return resp.json()
    else:
        error_data = resp.json()
        error_msg = error_data.get("error", {}).get("message", "Unknown error")
        raise ValueError(error_msg)
