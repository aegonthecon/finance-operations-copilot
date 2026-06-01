# backend/app/schemas.py
"""Pydantic schemas for request/response validation.
Only essential fields are defined for the demo.
"""
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional

class InvoiceUploadResponse(BaseModel):
    message: str = Field(..., example="Invoice uploaded successfully")
    invoice_id: int

class InvoiceExtractResponse(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    amount: Optional[float] = None
    currency: Optional[str] = None

class VendorClassificationResponse(BaseModel):
    category: str
    reasoning: str

class PriorityScoreResponse(BaseModel):
    priority_score: Optional[float] = None
    recommendation: str
    priority_reasoning: Optional[str] = None

class ReceivableUploadResponse(BaseModel):
    message: str = Field(..., example="Receivable data uploaded")
    count: int

class EmailDraftResponse(BaseModel):
    subject: str
    body: str

class ReceivableCreate(BaseModel):
    customer: str
    amount_due: float
    days_overdue: int

class FinanceIntelligence(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    category: Optional[str] = None
    classification_reasoning: Optional[str] = None
    priority_score: Optional[float] = None
    priority_reasoning: Optional[str] = None
    duplicate_risk: Optional[float] = None
    duplicate_reasoning: Optional[str] = None
    recommended_action: Optional[str] = None

class AnalyzeInvoiceResponse(BaseModel):
    message: str
    invoice_id: int
    data: FinanceIntelligence
