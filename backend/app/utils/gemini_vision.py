# backend/app/utils/gemini_vision.py
"""Utility for invoice OCR using Gemini Vision API.
If GEMINI_API_KEY is not set, returns mock data for demo purposes.
"""
import os
from typing import Dict, Any

# Load environment variables if .env exists
if os.path.exists(os.path.join(os.path.dirname(__file__), "../../../.env")):
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=API_KEY)
    vision_model = genai.GenerativeModel("gemini-pro-vision")
else:
    vision_model = None  # fallback mock

def extract_invoice(file_path: str) -> Dict[str, Any]:
    """Extract invoice fields from an image or PDF.
    Returns a dict with keys:
        invoice_number, vendor_name, invoice_date, due_date, amount, currency
    """
    if not API_KEY:
        # Mock response for demo when API key missing
        return {
            "invoice_number": "INV-00123",
            "vendor_name": "Acme Corp",
            "invoice_date": "2024-04-10",
            "due_date": "2024-05-10",
            "amount": 1250.00,
            "currency": "USD",
        }
    # Read file bytes
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    # Prepare prompt
    prompt = (
        "You are an OCR assistant. Extract the following fields from the invoice: "
        "invoice_number, vendor_name, invoice_date, due_date, amount, currency. "
        "Return a JSON object with these keys."
    )
    # Send to Gemini Vision API
    response = vision_model.generate_content([
        file_bytes,
        prompt,
    ])
    # The response text should be a JSON string; parse it safely
    try:
        import json
        data = json.loads(response.text)
    except Exception:
        # Fallback if parsing fails
        raise ValueError("Failed to parse Gemini Vision response as JSON")
    return data
