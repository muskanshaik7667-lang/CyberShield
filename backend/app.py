"""
CyberShield Backend — Flask API
================================
GET /scan   → Reads results.json from the project root and returns raw attack results.
GET /report → Returns a JSON summary with stats, severity score, and PASS results grouped by category.

Runs on port 5001 to avoid collision with target_app on 5000.
"""

import json
import os

from flask import Flask, jsonify
from flask_cors import CORS

from report_generator import generate_report

app = Flask(__name__)
CORS(app)  # Enable CORS for local frontend testing

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------
# results.json lives at the PROJECT ROOT (one level above /backend).
# Works whether you run `python app.py` from inside /backend or from the
# project root via `python backend/app.py`.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
RESULTS_PATH = os.path.join(_PROJECT_ROOT, "results.json")


def _load_results():
    """Read and parse results.json from the project root."""
    if not os.path.isfile(RESULTS_PATH):
        return None, f"results.json not found at {RESULTS_PATH}"
    try:
        with open(RESULTS_PATH, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data, None
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON in results.json: {exc}"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/scan", methods=["GET"])
def scan():
    """
    Trigger a scan — for now, simply reads the latest results.json produced
    by the agent and returns the raw attack results.
    """
    results, error = _load_results()
    if error:
        return jsonify({"status": "error", "message": error}), 404

    return jsonify({
        "status": "success",
        "message": "Scan results loaded successfully.",
        "total": len(results),
        "results": results,
    })


@app.route("/report", methods=["GET"])
def report():
    """
    Return a JSON summary: total attacks, PASS/FAIL counts, PASS rate %,
    severity score, and PASS results grouped by category.
    """
    results, error = _load_results()
    if error:
        return jsonify({"status": "error", "message": error}), 404

    summary = generate_report(results)
    return jsonify({"status": "success", "report": summary})


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"[CyberShield] Loading results from: {RESULTS_PATH}")
    app.run(host="0.0.0.0", port=5001, debug=True)
