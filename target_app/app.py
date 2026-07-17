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
    api_key = (
        os.environ.get("AQ.Ab8RN6KCkoeTuYd9IW2faSN1a3BJNBx95zG-n2B9N7GTKDI70Q")
        or os.environ.get("GEMINI_API_KEY")
        or "AQ.Ab8RN6KCkoeTuYd9IW2faSN1a3BJNBx95zG-n2B9N7GTKDI70Q"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_message}"}]}],
        "generationConfig": {"maxOutputTokens": 500}
    }
    resp = requests.post(url, headers={"content-type": "application/json"}, json=payload)
    if resp.status_code == 200:
        candidates = resp.json().get("candidates", [])
        reply = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "") if candidates else ""
        return jsonify({"response": reply, "status": "success"})
    return jsonify({"error": resp.text, "status_code": resp.status_code}), resp.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
