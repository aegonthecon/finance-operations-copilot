# backend/app/utils/vendor_classify.py
"""Utility to classify vendor categories using Gemini Flash.
If GEMINI_API_KEY is missing, returns a deterministic mock classification.
"""
import os
from typing import Dict

if os.path.exists(os.path.join(os.path.dirname(__file__), "../../../.env")):
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    flash_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    flash_model = None

CATEGORIES = ["Infrastructure", "Marketing", "Software", "Contractors", "Logistics", "Miscellaneous"]

def classify_vendor(vendor_name: str) -> Dict[str, str]:
    """Return a category and a short reasoning for the given vendor.
    Mock mode returns the first category with a generic reason.
    """
    if not API_KEY:
        return {"category": CATEGORIES[0], "reasoning": f"{vendor_name} is classified based on mock rules as {CATEGORIES[0]}"}
    prompt = (
        f"Classify the vendor '{vendor_name}' into one of the following categories: {', '.join(CATEGORIES)}. "
        "Provide the chosen category and a one‑sentence reasoning. "
        "Return a JSON object with keys 'category' and 'reasoning'."
    )
    response = flash_model.generate_content(prompt)
    try:
        import json
        data = json.loads(response.text)
    except Exception:
        raise ValueError("Failed to parse Gemini Flash response as JSON")
    return data
