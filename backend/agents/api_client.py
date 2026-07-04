import os
import json
import urllib.request
import urllib.error
import time


def get_api_key() -> str:
    """Load API Key from environment or .env file (checks API_KEY and GEMINI_API_KEY)."""
    key = os.environ.get("API_KEY") or os.environ.get("GEMINI_API_KEY")
    if key:
        return key

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
                        if line_str.startswith("API_KEY="):
                            return line_str.split("=", 1)[1].strip()
                        elif line_str.startswith("GEMINI_API_KEY="):
                            return line_str.split("=", 1)[1].strip()
            except Exception:
                pass
    return ""


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
    """Call the Gemini API. Raises ValueError on quota limits, missing keys, or timeouts."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "No API key found. Please set API_KEY=your_key in your .env file."
        )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.5-flash:generateContent?key={api_key}"
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
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    max_retries = 3

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
                # Daily quota exhausted — retrying is pointless, fail immediately
                if _is_daily_quota_exhausted(error_body):
                    raise ValueError(
                        "Your API key's daily quota is fully used up for today.\n"
                        "Fix: Go to https://aistudio.google.com/app/apikey, "
                        "create a NEW API key, and replace it in your .env file "
                        "as: API_KEY=your_new_key_here"
                    ) from e

                # Per-minute rate limit — wait the delay the API tells us, then retry
                if attempt < max_retries - 1:
                    wait_time = _parse_retry_delay(error_body)
                    time.sleep(wait_time)
                    continue

                raise ValueError(
                    "Per-minute API rate limit reached. Please wait 30 seconds and try again."
                ) from e

            raise ValueError(f"API Error ({e.code}): {error_body}") from e

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise ValueError(f"API call failed: {e}") from e
