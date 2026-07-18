from dotenv import load_dotenv
import os
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_message = data.get("message") or data.get("prompt") or ""
    prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read().strip()
    keys_str = os.environ.get("GEMINI_API_KEYS", "").strip()
    if keys_str:
        api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
    else:
        single_key = os.environ.get("GEMINI_API_KEY", "").strip()
        api_keys = [single_key] if single_key else []
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_message}"}]}],
        "generationConfig": {"maxOutputTokens": 500}
    }
    last_resp = None
    for api_key in api_keys:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        resp = requests.post(url, headers={"content-type": "application/json"}, json=payload)
        last_resp = resp
        if resp.status_code == 200:
            candidates = resp.json().get("candidates", [])
            reply = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "") if candidates else ""
            return jsonify({"response": reply, "status": "success"})
        elif resp.status_code == 429:
            continue
        else:
            break
    if last_resp is not None:
        return jsonify({"error": last_resp.text, "status_code": last_resp.status_code}), last_resp.status_code
    return jsonify({"error": "No API keys configured", "status_code": 500}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
