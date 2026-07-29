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
from db import supabase

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


def _save_results_to_db(scan_id, results):
    """Save agent results to Supabase results table."""
    rows = []
    for item in results:
        rows.append({
            "scan_id": scan_id,
            "attack_id": item.get("id", ""),
            "category": item.get("category", ""),
            "payload": item.get("payload", ""),
            "target_response": item.get("target_response", ""),
            "verdict": item.get("verdict", "FAIL"),
            "reason": item.get("reason", "")
        })
    supabase.table("results").insert(rows).execute()

def _load_results_from_db(scan_id):
    """Load results from Supabase for a given scan_id."""
    response = supabase.table("results")\
        .select("*")\
        .eq("scan_id", scan_id)\
        .execute()
    return response.data or []

def _create_scan(target_url):
    """Create a new scan record in Supabase and return its id."""
    response = supabase.table("scans").insert({
        "target_url": target_url,
        "status": "running"
    }).execute()
    return response.data[0]["id"]

def _complete_scan(scan_id):
    """Mark a scan as completed in Supabase."""
    from datetime import datetime, timezone
    supabase.table("scans").update({
        "status": "completed",
        "completed_at": datetime.now(timezone.utc).isoformat()
    }).eq("id", scan_id).execute()

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
        target_url = data.get("target_url", "http://localhost:5000/chat")
        
        # Create scan record in Supabase
        scan_id = _create_scan(target_url)
        
        # Back up current good results before overwriting
        current_results, current_error = _load_results()
        if not current_error and current_results:
            is_good = any(
                "classifier api error" not in r.get("reason", "").lower() and
                "quota" not in r.get("reason", "").lower()
                for r in current_results
            )
            if is_good:
                import shutil
                shutil.copy2(RESULTS_PATH, os.path.join(_PROJECT_ROOT, "results_last_good.json"))
        
        try:
            agent_module.run_evaluation(target_url=target_url)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Agent evaluation failed: {str(e)}"}), 500
        
        # Load fresh results from file and save to Supabase
        results, error = _load_results()
        if not error and results:
            _save_results_to_db(scan_id, results)
            _complete_scan(scan_id)
        
        # Store scan_id in a temp file so GET /scan can retrieve it
        scan_id_path = os.path.join(_PROJECT_ROOT, "last_scan_id.txt")
        with open(scan_id_path, "w") as f:
            f.write(scan_id)

    # Try loading from Supabase first
    scan_id_path = os.path.join(_PROJECT_ROOT, "last_scan_id.txt")
    results = []
    if os.path.isfile(scan_id_path):
        with open(scan_id_path, "r") as f:
            last_scan_id = f.read().strip()
        results = _load_results_from_db(last_scan_id)

    # Fall back to results.json if Supabase returns nothing
    if not results:
        results, error = _load_results()
        if error:
            return jsonify({"status": "error", "message": error}), 404

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
