from utils.firebase_manager import get_db

def load_user_profile(user_uid: str) -> dict:
    """Load the persistent user profile from Firestore."""
    if not user_uid:
        return {"allergies": [], "diet": "", "likes": [], "dislikes": []}
        
    db = get_db()
    doc_ref = db.collection("users").document(user_uid)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        # Ensure default keys exist
        return {
            "allergies": data.get("allergies", []),
            "diet": data.get("diet", ""),
            "likes": data.get("likes", []),
            "dislikes": data.get("dislikes", [])
        }
            
    # Default empty profile
    return {
        "allergies": [],
        "diet": "",
        "likes": [],
        "dislikes": []
    }

def save_user_profile(user_uid: str, profile: dict):
    """Save the user profile to Firestore."""
    if not user_uid:
        return
    db = get_db()
    db.collection("users").document(user_uid).set(profile)

def update_user_profile(user_uid: str, new_prefs: dict) -> dict:
    """
    Merge newly extracted preferences with the existing profile.
    Returns the updated, fully merged profile.
    """
    if not user_uid:
        return new_prefs
        
    profile = load_user_profile(user_uid)
    
    # Helper to merge lists without case-sensitive duplicates
    def merge_lists(existing: list, incoming: list) -> list:
        result = list(existing)
        existing_lower = [item.lower() for item in existing]
        for item in incoming:
            if item.lower() not in existing_lower:
                result.append(item)
                existing_lower.append(item.lower())
        return result

    profile["allergies"] = merge_lists(profile.get("allergies", []), new_prefs.get("allergies", []))
    profile["likes"] = merge_lists(profile.get("likes", []), new_prefs.get("likes", []))
    profile["dislikes"] = merge_lists(profile.get("dislikes", []), new_prefs.get("dislikes", []))
    
    # Overwrite diet if a new one is specified
    if new_prefs.get("diet"):
        profile["diet"] = new_prefs.get("diet")
        
    save_user_profile(user_uid, profile)
    return profile
