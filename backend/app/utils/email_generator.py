# backend/app/utils/email_generator.py
"""Utility to generate follow‑up reminder emails using Gemini Flash.
Falls back to a mock template when GEMINI_API_KEY is not set.
"""
import os
import json
from typing import Dict

if os.path.exists(os.path.join(os.path.dirname(__file__), "../../../.env")):
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "../../../.env"))

API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=API_KEY)
else:
    client = None

def generate_email(customer: str, invoice_number: str, amount: float, due_date: str, currency: str, reminder_type: str = "Friendly") -> Dict[str, str]:
    """Return a subject and body for a payment reminder email.
    Mock mode returns a simple templated email.
    """
    if not API_KEY:
        subject = f"{reminder_type} Reminder: Invoice {invoice_number} due"
        body = (
            f"Dear {customer},\n\n"
            f"We hope you are well. This is a {reminder_type.lower()} reminder that invoice {invoice_number} "
            f"for {currency} {amount:,.2f} was due on {due_date}. Please let us know if you need any "
            "further information or assistance.\n\n"
            "Thank you for your prompt attention.\n\n"
            "Best regards,\nFinance Team"
        )
        return {"subject": subject, "body": body}
    
    prompt = (
        f"Compose a professional {reminder_type.lower()} payment reminder email for a customer. "
        f"Customer: {customer}\nInvoice: {invoice_number}\nAmount: {currency} {amount}\nDue Date: {due_date}\n"
    )
    if reminder_type.lower() == "friendly":
        prompt += "The tone should be polite, friendly, and assume they just forgot."
    elif reminder_type.lower() == "second":
        prompt += "The tone should be firm but professional, asking for an immediate status update."
    elif reminder_type.lower() == "final":
        prompt += "The tone should be very urgent and firm, mentioning that further action may be taken if not paid immediately."
        
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "subject": {"type": "STRING"},
                        "body": {"type": "STRING"}
                    },
                    "required": ["subject", "body"]
                }
            ),
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"Email generation failed: {e}")
        return {"subject": f"Error generating email", "body": str(e)}
