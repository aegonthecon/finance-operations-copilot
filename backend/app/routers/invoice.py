# backend/app/routers/invoice.py
"""Invoice related API routes.
Endpoints:
- POST /invoice/upload : Accepts a file upload, saves it, runs OCR, stores record.
- GET /invoice/{invoice_id}/extract : Returns extracted fields.
- GET /invoice/{invoice_id}/classify : Returns vendor classification.
- GET /invoice/{invoice_id}/priority : Returns priority score and recommendation.
- GET /invoice/{invoice_id}/duplicate : Returns duplicate flag.
"""
import os
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..utils import gemini_vision, vendor_classify, priority  # priority utility will be created later
from datetime import date

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=schemas.InvoiceUploadResponse)
def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    # Create DB entry with file_path
    db_invoice = models.Invoice(file_path=file_path)
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return schemas.InvoiceUploadResponse(message="Invoice uploaded", invoice_id=db_invoice.id)

@router.get("/{invoice_id}/extract", response_model=schemas.InvoiceExtractResponse)
def extract_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    # Perform OCR if not already extracted
    if not invoice.invoice_number:
        data = gemini_vision.extract_invoice(invoice.file_path)
        invoice.invoice_number = data.get("invoice_number")
        invoice.vendor_name = data.get("vendor_name")
        # Parse ISO date strings to Python date objects for SQLite
        inv_date_str = data.get("invoice_date")
        due_date_str = data.get("due_date")
        invoice.invoice_date = date.fromisoformat(inv_date_str) if inv_date_str else None
        invoice.due_date = date.fromisoformat(due_date_str) if due_date_str else None
        invoice.amount = data.get("amount")
        invoice.currency = data.get("currency")
        db.commit()
    return schemas.InvoiceExtractResponse(
        invoice_number=invoice.invoice_number,
        vendor_name=invoice.vendor_name,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        amount=invoice.amount,
        currency=invoice.currency,
    )

@router.get("/{invoice_id}/classify", response_model=schemas.VendorClassificationResponse)
def classify_vendor_route(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    if not invoice.vendor_name:
        raise HTTPException(status_code=400, detail="Vendor name not extracted yet")
    result = vendor_classify.classify_vendor(invoice.vendor_name)
    invoice.vendor_category = result["category"]
    invoice.vendor_reasoning = result["reasoning"]
    db.commit()
    return schemas.VendorClassificationResponse(**result)

@router.get("/{invoice_id}/priority", response_model=schemas.PriorityScoreResponse)
def priority_score(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    # Ensure necessary fields exist
    if not all([invoice.due_date, invoice.vendor_category, invoice.amount]):
        raise HTTPException(status_code=400, detail="Missing data for priority calculation")
    score, rec = priority.calculate_priority(
        due_date=invoice.due_date,
        vendor_category=invoice.vendor_category,
        amount=invoice.amount,
        risk_notes=invoice.vendor_reasoning or "",
    )
    invoice.priority_score = score
    db.commit()
    return schemas.PriorityScoreResponse(priority_score=score, recommendation=rec)

@router.get("/{invoice_id}/duplicate")
def duplicate_check(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    # Simple duplicate detection based on invoice_number and vendor_name
    dup = (
        db.query(models.Invoice)
        .filter(models.Invoice.id != invoice.id)
        .filter(models.Invoice.invoice_number == invoice.invoice_number)
        .filter(models.Invoice.vendor_name == invoice.vendor_name)
        .first()
    )
    flag = dup is not None
    invoice.duplicate_flag = flag
    db.commit()
    return {"duplicate": flag}
