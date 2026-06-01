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
from ..utils import gemini_vision, vendor_classify, priority, finance_intelligence
from datetime import date, datetime

router = APIRouter()

@router.get("")
def list_invoices(db: Session = Depends(get_db)):
    return db.query(models.Invoice).all()

# Debug endpoint to clear the in‑memory classification cache (use in development only)
@router.get("/classify/clear_cache", response_model=dict)
def clear_classification_cache():
    from ..utils import vendor_classify
    vendor_classify._classification_cache.clear()
    logging.info("Classification cache cleared via debug endpoint")
    return {"status": "cache_cleared"}

def parse_date(value):
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    try:
        return datetime.strptime(value, "%d %B %Y").date()
    except ValueError:
        return None

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

@router.post("/analyze", response_model=schemas.AnalyzeInvoiceResponse)
def analyze_invoice_route(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    # Run unified analysis
    try:
        data = finance_intelligence.analyze_invoice(file_path)
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Gemini analysis temporarily unavailable")
    
    # Create DB entry
    db_invoice = models.Invoice(
        file_path=file_path,
        invoice_number=data.get("invoice_number"),
        vendor_name=data.get("vendor_name"),
        invoice_date=parse_date(data.get("invoice_date")),
        due_date=parse_date(data.get("due_date")),
        amount=data.get("amount"),
        currency=data.get("currency"),
        vendor_category=data.get("category"),
        vendor_reasoning=data.get("classification_reasoning"),
        priority_score=data.get("priority_score"),
        priority_reasoning=data.get("priority_reasoning"),
        duplicate_risk=data.get("duplicate_risk"),
        duplicate_reasoning=data.get("duplicate_reasoning"),
        recommended_action=data.get("recommended_action"),
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    
    return schemas.AnalyzeInvoiceResponse(
        message="Invoice analyzed successfully",
        invoice_id=db_invoice.id,
        data=schemas.FinanceIntelligence(**data)
    )

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
        invoice.invoice_date = parse_date(inv_date_str)
        invoice.due_date = parse_date(due_date_str)
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
    if not invoice.vendor_category:
        result = vendor_classify.classify_vendor(invoice.vendor_name, amount=invoice.amount)
        invoice.vendor_category = result["category"]
        invoice.vendor_reasoning = result["reasoning"]
        db.commit()
    else:
        result = {
            "category": invoice.vendor_category,
            "reasoning": invoice.vendor_reasoning or ""
        }
    return schemas.VendorClassificationResponse(**result)

@router.get("/{invoice_id}/priority", response_model=schemas.PriorityScoreResponse)
def priority_score(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    if invoice.priority_score is None:
        # Run AI-first analysis to compute priority and other missing fields
        try:
            data = finance_intelligence.analyze_invoice(invoice.file_path)
        except RuntimeError:
            return schemas.PriorityScoreResponse(
                priority_score=None,
                recommendation="Analysis unavailable",
                priority_reasoning="All Gemini models were temporarily unavailable."
            )
        
        # Populate all fields extracted by the AI
        invoice.invoice_number = invoice.invoice_number or data.get("invoice_number")
        invoice.vendor_name = invoice.vendor_name or data.get("vendor_name")
        if not invoice.invoice_date:
            invoice.invoice_date = parse_date(data.get("invoice_date"))
        if not invoice.due_date:
            invoice.due_date = parse_date(data.get("due_date"))
        invoice.amount = invoice.amount or data.get("amount")
        invoice.currency = invoice.currency or data.get("currency")
        
        invoice.vendor_category = invoice.vendor_category or data.get("category")
        invoice.vendor_reasoning = invoice.vendor_reasoning or data.get("classification_reasoning")
        
        invoice.priority_score = data.get("priority_score")
        invoice.priority_reasoning = data.get("priority_reasoning")
        invoice.duplicate_risk = data.get("duplicate_risk")
        invoice.duplicate_reasoning = data.get("duplicate_reasoning")
        invoice.recommended_action = data.get("recommended_action")
        
        db.commit()
        
    score = invoice.priority_score
    rec = invoice.recommended_action or "Investigate"
    reasoning = invoice.priority_reasoning
    
    return schemas.PriorityScoreResponse(
        priority_score=score, 
        recommendation=rec, 
        priority_reasoning=reasoning
    )

@router.get("/{invoice_id}/duplicate")
def duplicate_check(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    if invoice.duplicate_risk is not None:
        flag = invoice.duplicate_risk > 0.5
        invoice.duplicate_flag = flag
        db.commit()
        return {
            "duplicate": flag, 
            "risk_score": invoice.duplicate_risk, 
            "reasoning": invoice.duplicate_reasoning
        }

    # Simple duplicate detection based on invoice_number and vendor_name (legacy)
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
