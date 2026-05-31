# backend/app/utils/priority.py
"""Utility to compute payment priority scores.
The formula (as defined in the PRD):
    priority = 0.4 * due_date_urgency + 0.3 * vendor_criticality + 0.2 * amount_score + 0.1 * risk_score
We map textual categories to numeric criticality values.
"""
import datetime
from typing import Tuple

# Mapping of vendor categories to criticality (0‑100)
CRITICALITY_MAP = {
    "Infrastructure": 90,
    "Marketing": 60,
    "Software": 80,
    "Contractors": 70,
    "Logistics": 50,
    "Miscellaneous": 30,
}

def _date_urgency(due_date: datetime.date) -> float:
    """Return a score (0‑100) based on how soon the due date is.
    - If due within 7 days → 100
    - 8‑14 days → 80
    - 15‑30 days → 60
    - 31‑60 days → 40
    - >60 days → 20
    """
    today = datetime.date.today()
    delta = (due_date - today).days
    if delta <= 7:
        return 100.0
    if delta <= 14:
        return 80.0
    if delta <= 30:
        return 60.0
    if delta <= 60:
        return 40.0
    return 20.0

def _amount_score(amount: float) -> float:
    """Normalize amount to 0‑100 (capped at $100k)."""
    cap = 100_000.0
    return min(100.0, (amount / cap) * 100)

def _risk_score(reasoning: str) -> float:
    """Very simple heuristic: if reasoning mentions 'high' risk, lower score.
    Returns 0‑100 where higher is better (lower risk).
    """
    lowered = reasoning.lower()
    if "high" in lowered or "risk" in lowered:
        return 30.0
    if "medium" in lowered:
        return 60.0
    return 90.0

def calculate_priority(due_date: datetime.date, vendor_category: str, amount: float, risk_notes: str) -> Tuple[float, str]:
    """Calculate priority score and textual recommendation.
    Returns (score, recommendation).
    """
    due_score = _date_urgency(due_date)
    crit_score = CRITICALITY_MAP.get(vendor_category, 30)
    amt_score = _amount_score(amount)
    risk_score = _risk_score(risk_notes)

    priority = (
        0.4 * due_score +
        0.3 * crit_score +
        0.2 * amt_score +
        0.1 * risk_score
    )
    # Recommendation based on score ranges
    if priority >= 85:
        rec = "Pay immediately"
    elif priority >= 65:
        rec = "Schedule soon"
    else:
        rec = "Can be delayed"
    return round(priority, 2), rec
