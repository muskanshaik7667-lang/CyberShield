import requests
import os
from dotenv import load_dotenv
load_dotenv()

resp = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}"}
)
models = resp.json().get("data", [])
free_models = [m["id"] for m in models if ":free" in m["id"]]
print("FREE MODELS:")
print(free_models)
