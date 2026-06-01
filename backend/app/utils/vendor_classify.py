# backend/app/utils/vendor_classify.py
"""Utility to classify vendor categories using Gemini Flash.
If GEMINI_API_KEY is missing, returns a deterministic mock classification.
"""

import os
import json
import re
import logging
import time
from typing import Dict, Optional

# Load .env from project root if present
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
if os.path.exists(env_path):
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path)
    except ImportError:
        logging.warning("python-dotenv not installed; .env will not be loaded")

API_KEY = os.getenv("GEMINI_API_KEY")

# Initialise Gemini client when API key is available
if API_KEY:
    from google import genai
    client = genai.Client(api_key=API_KEY)
else:
    client = None

CATEGORIES = ["Infrastructure", "Marketing", "Software", "Contractors", "Logistics", "Miscellaneous"]

# In‑memory cache for successful classifications (vendor_name → result)
_classification_cache: Dict[str, Dict[str, str]] = {}

# Retry configuration
_BASE_BACKOFF = 1.0  # seconds
_MAX_RETRIES = 3

def _mock_classify(vendor_name: str) -> Dict[str, str]:
    """Deterministic mock classification used when no Gemini API key is set.
    Returns the first category as a placeholder.
    """
    logging.info("Using mock classification for vendor: %s", vendor_name)
    return {
        "category": CATEGORIES[0],
        "reasoning": f"{vendor_name} is classified based on mock rules as {CATEGORIES[0]}",
    }

def classify_vendor(vendor_name: str, amount: Optional[float] = None) -> Dict[str, str]:
    """Classify a vendor name into a predefined category using Gemini Flash.

    Returns a dict with keys ``category`` and ``reasoning``. If the Gemini call
    fails or the API key is missing, a deterministic mock classification is used.
    """
    logging.info("Classifying vendor '%s' (amount: %s) using Gemini", vendor_name, amount)

    # Return cached result if we have one
    if vendor_name in _classification_cache:
        logging.info("Cache hit for vendor '%s': %s", vendor_name, _classification_cache[vendor_name])
        return _classification_cache[vendor_name]

    if not client:
        logging.warning("Gemini client not initialized; using mock classification")
        result = _mock_classify(vendor_name)
        _classification_cache[vendor_name] = result
        return result

    # Reuse the same candidate model list as OCR, but limit attempts to first 2 models
    try:
        from .gemini_vision import CANDIDATE_MODELS
    except Exception:
        CANDIDATE_MODELS = ["models/gemini-2.5-flash"]

    limited_models = CANDIDATE_MODELS

    extra_context = f" The invoice amount is ${amount:.2f}." if amount is not None else ""
    prompt = (
        f"Classify the vendor '{vendor_name}' into one of the following categories: {', '.join(CATEGORIES)}.{extra_context} "
        "Provide the chosen category and a one‑sentence reasoning. "
        "Return a JSON object with keys 'category' and 'reasoning'."
    )
    logging.debug("Gemini classification prompt: %s", prompt[:200])

    for model_name in limited_models:
        logging.info("Attempting Gemini classification with model %s", model_name)
        attempt = 0
        while attempt < _MAX_RETRIES:
            attempt += 1
            try:
                response = client.models.generate_content(model=model_name, contents=[prompt])
            except Exception as exc:
                # Detect transient HTTP errors (503, 429)
                status_code = getattr(exc, "status_code", None)
                if status_code in (503, 429):
                    # Respect Retry‑After header if present
                    retry_after = getattr(exc, "retry_after", None)
                    delay = float(retry_after) if retry_after else _BASE_BACKOFF * (2 ** (attempt - 1))
                    logging.warning(
                        "Transient Gemini error %s on model %s (attempt %d/%d); sleeping %.2f sec",
                        status_code,
                        model_name,
                        attempt,
                        _MAX_RETRIES,
                        delay,
                    )
                    time.sleep(delay)
                    continue  # retry the same model
                else:
                    logging.error(
                        "Gemini classification request raised non‑transient exception for model %s: %s",
                        model_name,
                        exc,
                    )
                    break  # move to next model
            else:
                # Successful response – process it
                resp_text = getattr(response, "text", None)
                if resp_text is None:
                    try:
                        resp_text = response.parts[0].text
                    except Exception:
                        resp_text = str(response)
                logging.debug("Gemini raw response: %s", resp_text)
                clean_text = resp_text.strip()
                clean_text = re.sub(r"^```json\s*", "", clean_text)
                clean_text = re.sub(r"\s*```$", "", clean_text)
                try:
                    data = json.loads(clean_text)
                    logging.info("Gemini classification succeeded with model %s: %s", model_name, data)
                    _classification_cache[vendor_name] = data
                    return data
                except Exception as exc:
                    logging.error(
                        "Failed to parse classification JSON for model %s: %s",
                        model_name,
                        exc,
                    )
                    break  # move to next model
        # Exhausted retries for this model – try next one
        logging.warning("Exhausted retries for model %s", model_name)
    # All models failed – fall back to mock classification and cache it
    logging.warning("All Gemini models failed; falling back to mock classification for vendor %s", vendor_name)
    result = _mock_classify(vendor_name)
    _classification_cache[vendor_name] = result
    return result
