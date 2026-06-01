# backend/app/utils/finance_intelligence.py
import os
import json
import logging
import re
from typing import Dict, Any
from google import genai

from pathlib import Path
env_path = Path(__file__).resolve().parents[2] / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

client = genai.Client(api_key=API_KEY)
logger = logging.getLogger(__name__)

# Reusing the same models that have been working
CANDIDATE_MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-pro",
    "models/gemini-pro-latest",
    "models/gemini-3.5-flash",
    "models/gemini-3-pro-image",
]

def analyze_invoice(file_path: str) -> Dict[str, Any]:
    """Single multimodal Gemini Vision call to extract all Finance Intelligence."""
    
    prompt = (
        "Read the attached invoice image and analyze it as a Finance Copilot. "
        "Extract the following values and provide assessments based on the invoice context. "
        "Return valid JSON with exactly these fields:\n"
        "- invoice_number (string or null)\n"
        "- vendor_name (string or null)\n"
        "- invoice_date (YYYY-MM-DD or null)\n"
        "- due_date (YYYY-MM-DD or null)\n"
        "- amount (number or null)\n"
        "- currency (string or null)\n"
        "- category (string): Classify the vendor based on the invoice context. "
        "Choose from: Meals & Entertainment, Travel, Office Supplies, E-commerce, Professional Services, Infrastructure, Software, Miscellaneous, or create a fitting one.\n"
        "- classification_reasoning (string): Explain why this category was chosen.\n"
        "- priority_score (number between 0 and 1): Rate how urgent it is to pay this invoice. Higher means more urgent.\n"
        "- priority_reasoning (string): Explain the priority score.\n"
        "- duplicate_risk (number between 0 and 1): Estimate the risk of this being a duplicate (0 if it looks like a standard original invoice).\n"
        "- duplicate_reasoning (string): Explain the duplicate risk.\n"
        "- recommended_action (string): Action to take. Choose from: 'Pay Immediately', 'Standard Processing', 'Review for Duplicate', 'Escalate for Approval', 'Investigate'.\n"
        "\nDo not include any Markdown formatting like ```json in your response, just return the raw JSON object."
    )

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    for model_name in CANDIDATE_MODELS:
        logger.info("Attempting full analysis with model %s", model_name)
        try:
            uploaded_file = client.files.upload(file=file_path)
            
            response = client.models.generate_content(
                model=model_name,
                contents=[prompt, uploaded_file]
            )
            
            resp_text = getattr(response, "text", None)
            if resp_text is None:
                try:
                    resp_text = response.parts[0].text
                except Exception:
                    resp_text = str(response)

            clean_text = resp_text.strip()
            clean_text = re.sub(r"^```json\s*", "", clean_text)
            clean_text = re.sub(r"\s*```$", "", clean_text)
            
            data = json.loads(clean_text)
            logger.info("Analysis successful with model %s", model_name)
            return data
        except Exception as exc:
            logger.error("Model %s failed: %s", model_name, exc)
            continue

    raise RuntimeError("All candidate Gemini models failed for unified analysis")
