import os
import json
import requests
import firebase_admin
from firebase_admin import credentials, firestore

# (API Key removed as auth is no longer used)

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

# Auth functions removed.
