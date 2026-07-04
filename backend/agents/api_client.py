import os
import json
import urllib.request
import urllib.error

def get_api_key() -> str:
    """Load API Key from environment or .env file (checks API_KEY and GEMINI_API_KEY)."""
    # 1. Check OS Environment
    key = os.environ.get("API_KEY") or os.environ.get("GEMINI_API_KEY")
    if key:
        return key
        
    # 2. Check .env in parent or current directory
    base_dirs = [
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # root directory
        os.path.dirname(os.path.abspath(__file__)),                  # agents directory
        os.getcwd()                                                  # working directory
    ]
    for d in base_dirs:
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line_str = line.strip()
                        if line_str.startswith("API_KEY="):
                            return line_str.split("=", 1)[1].strip()
                        elif line_str.startswith("GEMINI_API_KEY="):
                            return line_str.split("=", 1)[1].strip()
            except Exception:
                pass
    return ""

def call_api(prompt: str = None, json_mode: bool = True, system_instruction: str = None, messages: list = None) -> str:
    """Call the generative API. Raises ValueError on quota limits, missing keys, or timeouts."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Quota full! Please try again later.")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    body = {}
    
    if system_instruction:
        body["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    if messages:
        gemini_contents = []
        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else "user"
            
            # Gemini strictly requires alternating roles. 
            # If the current role matches the previous role, merge their content.
            if gemini_contents and gemini_contents[-1]["role"] == role:
                gemini_contents[-1]["parts"][0]["text"] += f"\n\n{msg['content']}"
            else:
                gemini_contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
        body["contents"] = gemini_contents
    elif prompt:
        body["contents"] = [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]
    else:
        raise ValueError("Either prompt or messages must be provided.")
    
    if json_mode:
        body["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        # 10-second timeout for prompt execution
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = response.read().decode("utf-8")
            res_json = json.loads(res_data)
            text_response = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean markdown code block wraps if JSON mode is active
            if json_mode and text_response.startswith("```"):
                lines = text_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                text_response = "\n".join(lines).strip()
                
            return text_response
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        if e.code == 429:
            raise ValueError("Genie is a bit overwhelmed! The API rate limit was reached. Please wait a minute and try again.") from e
        raise ValueError(f"API Error ({e.code}): {error_body}") from e
    except Exception as e:
        raise ValueError(f"API call failed: {e}") from e
