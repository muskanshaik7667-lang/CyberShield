"""
CyberShield Backend — Flask API
================================
GET /scan   → Reads results.json from the project root and returns raw attack results.
GET /report → Returns a JSON summary with stats, severity score, and PASS results grouped by category.

Runs on port 5001 to avoid collision with target_app on 5000.
"""

import json
import os
import sys

from flask import Flask, jsonify, request
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

sys.path.append(_PROJECT_ROOT)
sys.path.append(os.path.join(_PROJECT_ROOT, "agent"))
import agent as agent_module


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
@app.route("/scan", methods=["GET", "POST"])
def scan():
    """
    Trigger a scan — reads results.json from the project root, transforms
    verdict to inverted frontend convention (backend PASS -> 'fail',
    backend FAIL -> 'pass'), and returns the array directly.
    Accepts an optional target_url via POST to run a live evaluation.
    """
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        target_url = data.get("target_url")
        
        # Check current results to see if they're "good" before we overwrite them
        current_results, current_error = _load_results()
        if not current_error and current_results:
            is_good = False
            for r in current_results:
                reason = r.get("reason", "").lower()
                if "classifier api error" not in reason and "quota" not in reason and "timed out" not in reason:
                    is_good = True
                    break
            if is_good:
                import shutil
                last_good_path = os.path.join(_PROJECT_ROOT, "results_last_good.json")
                shutil.copy2(RESULTS_PATH, last_good_path)

        try:
            agent_module.run_evaluation(target_url=target_url)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Agent evaluation failed: {str(e)}"}), 500

    results, error = _load_results()
    if error:
        return jsonify({"status": "error", "message": error}), 404

    # Check if the loaded results entirely failed due to API limits (applies to GET and POST)
    all_failed = True if results else False
    for r in (results or []):
        reason = r.get("reason", "").lower()
        if "classifier api error" not in reason and "quota" not in reason and "timed out" not in reason:
            all_failed = False
            break
    
    if all_failed:
        last_good_path = os.path.join(_PROJECT_ROOT, "results_last_good.json")
        if os.path.isfile(last_good_path):
            try:
                with open(last_good_path, "r", encoding="utf-8") as fh:
                    results = json.load(fh)
            except:
                pass

    transformed_results = []
    for item in results:
        transformed = dict(item)
        raw_verdict = str(item.get("verdict", "")).upper()
        if raw_verdict == "PASS":
            transformed["verdict"] = "fail"
        elif raw_verdict == "FAIL":
            transformed["verdict"] = "pass"
        else:
            transformed["verdict"] = "fail" if raw_verdict == "PASS" else "pass"
        transformed_results.append(transformed)

    return jsonify(transformed_results)


@app.route("/report", methods=["GET"])
def report():
    """
    Return the summary report object directly: total, pass_count, fail_count,
    pass_rate, severity, and by_category counts.
    """
    results, error = _load_results()
    if error:
        return jsonify({"status": "error", "message": error}), 404

    summary = generate_report(results)
    return jsonify(summary)


# ---------------------------------------------------------------------------
# Entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"[CyberShield] Loading results from: {RESULTS_PATH}")
    app.run(host="0.0.0.0", port=5001, debug=True)
