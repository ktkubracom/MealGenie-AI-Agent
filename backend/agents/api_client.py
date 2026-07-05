import os
import json
import urllib.request
import urllib.error
import time


def get_all_api_keys() -> list:
    """Load all available API Keys from environment, Streamlit secrets, or .env file."""
    keys = []
    
    # 1. Try OS Environment Variables
    for k, v in os.environ.items():
        if "API_KEY" in k and v.strip() and v.strip() not in keys:
            keys.append(v.strip())
            
    # 2. Try Streamlit Secrets
    try:
        import streamlit as st
        for k in st.secrets:
            if "API_KEY" in k:
                val = st.secrets[k]
                if val and val not in keys:
                    keys.append(val)
    except Exception:
        pass

    # 3. Read .env files manually
    base_dirs = [
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        os.path.dirname(os.path.abspath(__file__)),
        os.getcwd(),
    ]
    for d in base_dirs:
        env_path = os.path.join(d, ".env")
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line_str = line.strip()
                        if "API_KEY" in line_str and "=" in line_str:
                            val = line_str.split("=", 1)[1].strip()
                            # remove quotes if they exist
                            if val.startswith('"') and val.endswith('"'):
                                val = val[1:-1]
                            if val.startswith("'") and val.endswith("'"):
                                val = val[1:-1]
                            if val and val not in keys:
                                keys.append(val)
            except Exception:
                pass
                
    return keys


def _parse_retry_delay(error_body: str) -> float:
    """Extract retryDelay seconds from a 429 error body. Returns 30 if not found."""
    try:
        body = json.loads(error_body)
        details = body.get("error", {}).get("details", [])
        for detail in details:
            if "retryDelay" in detail:
                delay_str = detail["retryDelay"]
                return float(delay_str.replace("s", "").strip()) + 2
    except Exception:
        pass
    return 30.0


def _is_daily_quota_exhausted(error_body: str) -> bool:
    """Return True if the 429 is daily quota exhaustion, not a per-minute limit."""
    try:
        body = json.loads(error_body)
        details = body.get("error", {}).get("details", [])
        for detail in details:
            for v in detail.get("violations", []):
                if "PerDay" in v.get("quotaId", ""):
                    return True
        msg = body.get("error", {}).get("message", "")
        if "PerDay" in msg:
            return True
    except Exception:
        pass
    return False


def call_api(
    prompt: str = None,
    json_mode: bool = True,
    system_instruction: str = None,
    messages: list = None,
) -> str:
    """Call the Gemini API. Falls back to next key if quota is exhausted."""
    api_keys = get_all_api_keys()
    if not api_keys:
        raise ValueError(
            "No API keys found. Please set API_KEY=your_key in your .env file."
        )

    body = {}

    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    if messages:
        gemini_contents = []
        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else "user"
            if gemini_contents and gemini_contents[-1]["role"] == role:
                gemini_contents[-1]["parts"][0]["text"] += f"\n\n{msg['content']}"
            else:
                gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        body["contents"] = gemini_contents
    elif prompt:
        body["contents"] = [{"role": "user", "parts": [{"text": prompt}]}]
    else:
        raise ValueError("Either prompt or messages must be provided.")

    if json_mode:
        body["generationConfig"] = {"responseMimeType": "application/json"}

    data = json.dumps(body).encode("utf-8")
    
    last_error = None
    max_retries = 3

    # Try each available API key
    for api_key in api_keys:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.5-flash:generateContent?key={api_key}"
        )
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}, method="POST"
        )
        
        for attempt in range(max_retries):
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = response.read().decode("utf-8")
                    res_json = json.loads(res_data)
                    text_response = (
                        res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
                    )

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
                    # Daily quota exhausted — fail this key immediately, move to next key
                    if _is_daily_quota_exhausted(error_body):
                        last_error = f"Daily quota exhausted for key starting with {api_key[:5]}"
                        break 

                    # Per-minute rate limit — wait the delay the API tells us, then retry
                    if attempt < max_retries - 1:
                        wait_time = _parse_retry_delay(error_body)
                        time.sleep(wait_time)
                        continue

                    # If retries for rate limit fail, move to next key
                    last_error = "Per-minute API rate limit reached on all retries."
                    break

                # If it's a 400 Bad Request or similar, it's not a quota issue, raise immediately
                raise ValueError(f"API Error ({e.code}): {error_body}") from e

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                last_error = f"API call failed: {e}"
                break # Move to next key

    # If we exit the loop, all keys failed
    raise ValueError(f"All available API keys failed. Last error: {last_error}")
