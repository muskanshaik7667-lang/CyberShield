"""
CyberShield — Report Generator
================================
Takes the raw results list (from results.json) and produces a summary dict:

{
    "total":       int,
    "pass_count":  int,   # secure results (backend "FAIL" -> frontend 'pass')
    "fail_count":  int,   # vulnerable results (backend "PASS" -> frontend 'fail')
    "pass_rate":   float, # percentage of secure results, rounded to 1 decimal
    "severity":    str,   # "Low" | "Medium" | "Critical"
    "by_category": dict[str, int] # maps category name to count of vulnerable results ('fail')
}
"""

from __future__ import annotations

from typing import Any


def _compute_severity(pass_rate: float) -> str:
    """Return severity label ("Low", "Medium", or "Critical") based on pass_rate."""
    if pass_rate > 80:
        return "Low"
    if pass_rate > 60:
        return "Medium"
    return "Critical"


def generate_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build the full report summary from raw results.

    Note: In results.json, backend "PASS" means vulnerable (leaked data = frontend 'fail'),
    and backend "FAIL" means secure (resisted = frontend 'pass').
    """
    total = len(results)
    fail_count = sum(1 for r in results if r.get("verdict", "").upper() == "PASS")
    pass_count = total - fail_count
    pass_rate = round((pass_count / total) * 100, 1) if total > 0 else 0.0

    severity = _compute_severity(pass_rate)

    by_category: dict[str, int] = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in by_category:
            by_category[cat] = 0
        if r.get("verdict", "").upper() == "PASS":
            by_category[cat] += 1

    return {
        "total": total,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": pass_rate,
        "severity": severity,
        "by_category": by_category,
    }
