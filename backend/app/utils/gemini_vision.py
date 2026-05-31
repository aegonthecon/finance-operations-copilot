# backend/app/utils/gemini_vision.py
"""Utility for invoice OCR using Gemini Vision API.
Uses the google.genai SDK client (same code path as test_genai_connection.py).
Fallback is disabled – the function will raise if OCR fails.
"""

import os
import json
import logging
import hashlib
import datetime
import random
import re
from typing import Dict, Any

# Load environment variables (.env in project root)
from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
except ImportError:
    logging.warning("python-dotenv not installed; .env will not be loaded")

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

# Initialise Gemini client (the same as the standalone script)
from google import genai
client = genai.Client(api_key=API_KEY)

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Hard‑coded candidate models (order matters)
CANDIDATE_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    "models/gemini-pro-latest",
    "models/gemini-3.5-flash",
    "models/gemini-3-pro-image",
]

def _hash_based_mock(file_path: str) -> Dict[str, Any]:
    """Deterministic fallback – kept for safety but will not be used when fallback is disabled."""
    h = hashlib.sha256(file_path.encode()).hexdigest()
    inv_num = f"INV-{int(h[:6], 16) % 100000:05d}"
    vendor_name = f"Vendor-{h[:4]}"
    base_date = datetime.date(2024, 1, 1)
    offset = int(h[6:8], 16) % 365
    invoice_date = (base_date + datetime.timedelta(days=offset)).isoformat()
    due_date = (base_date + datetime.timedelta(days=offset + 30)).isoformat()
    amount = round((int(h[8:12], 16) % 10000) + 100 + random.random(), 2)
    currency = "USD"
    return {
        "invoice_number": inv_num,
        "vendor_name": vendor_name,
        "invoice_date": invoice_date,
        "due_date": due_date,
        "amount": amount,
        "currency": currency,
    }

def extract_invoice(file_path: str) -> Dict[str, Any]:
    """Extract invoice fields from an image or PDF using Gemini Vision.
    Returns a dict with keys: invoice_number, vendor_name, invoice_date, due_date, amount, currency.
    """
    # Prompt – identical to the standalone script
    prompt = (
        "Read the attached invoice image. Do not generate example values. "
        "Extract only values visible in the image and return valid JSON with the following fields: "
        "invoice_number, vendor_name, invoice_date, due_date, amount, currency."
    )

    logger.info("Starting OCR extraction for %s", file_path)

    # Ensure the file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Iterate over candidate models until one succeeds
    for model_name in CANDIDATE_MODELS:
        logger.info("Attempting OCR with model %s", model_name)
        try:
            # Upload the file using the client (keyword argument matches SDK signature)
            uploaded_file = client.files.upload(file=file_path)
            logger.info("Uploaded file ID: %s", getattr(uploaded_file, "name", "<no name>"))

            # Call generate_content (high‑level API) with prompt first
            response = client.models.generate_content(model=model_name, contents=[prompt, uploaded_file])
            logger.info("Raw Gemini response object: %s", response)

            # Extract response text
            resp_text = getattr(response, "text", None)
            if resp_text is None:
                # Fallback to parts if needed
                try:
                    resp_text = response.parts[0].text
                except Exception:
                    resp_text = str(response)
            logger.info("Gemini response text: %s", resp_text[:200])

            # Clean possible markdown fences before JSON parsing
            clean_text = resp_text.strip()
            clean_text = re.sub(r"^```json\s*", "", clean_text)
            clean_text = re.sub(r"\s*```$", "", clean_text)
            # Parse JSON
            data = json.loads(clean_text)
            logger.info("OCR extraction successful with model %s", model_name)
            return data
        except Exception as exc:
            logger.error("Model %s failed: %s", model_name, exc)
            # Continue to next candidate
            continue

    # All candidates failed – raise an error (fallback disabled)
    raise RuntimeError("All candidate Gemini models failed – fallback is disabled")

# End of gemini_vision.py
