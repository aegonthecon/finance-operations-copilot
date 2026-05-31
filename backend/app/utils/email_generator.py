# backend/app/utils/email_generator.py
"""Utility to generate follow‑up reminder emails using Gemini Flash.
Falls back to a mock template when GEMINI_API_KEY is not set.
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

def generate_email(customer: str, invoice_number: str, amount: float, due_date: str, currency: str) -> Dict[str, str]:
    """Return a subject and body for a payment reminder email.
    Mock mode returns a simple templated email.
    """
    if not API_KEY:
        subject = f"Reminder: Invoice {invoice_number} due"
        body = (
            f"Dear {customer},\n\n"
            f"We hope you are well. This is a friendly reminder that invoice {invoice_number} "
            f"for {currency} {amount:,.2f} was due on {due_date}. Please let us know if you need any "
            "further information or assistance.\n\n"
            "Thank you for your prompt attention.\n\n"
            "Best regards,\nFinance Team"
        )
        return {"subject": subject, "body": body}
    prompt = (
        f"Compose a professional payment reminder email for a customer. Include a subject line and body. "
        f"Customer: {customer}\nInvoice: {invoice_number}\nAmount: {currency} {amount}\nDue Date: {due_date}\n"
        "The tone should be polite and concise. Return a JSON object with keys 'subject' and 'body'."
    )
    response = flash_model.generate_content(prompt)
    try:
        import json
        data = json.loads(response.text)
    except Exception:
        raise ValueError("Failed to parse Gemini Flash email response as JSON")
    return data
