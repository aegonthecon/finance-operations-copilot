# backend/app/routers/receivable.py
"""Receivable related API routes.
Endpoints:
- POST /receivable/upload : Accept JSON list of receivables (customer, amount_due, days_overdue)
- GET /receivable/{receivable_id}/priority : Compute priority score for a receivable
- GET /receivable/{receivable_id}/email : Generate reminder email for a receivable
"""

import os
import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..utils import email_generator, priority as prio_util
from ..database import get_db

router = APIRouter()

@router.post("/upload", response_model=schemas.ReceivableUploadResponse)
def upload_receivables(
    data: List[schemas.ReceivableCreate] = Body(...),
    db: Session = Depends(get_db)
):
    # Expect list of dicts with keys: customer, amount_due, days_overdue
    count = 0
    for item in data:
        rec = models.Receivable(
            customer=item.customer,
            amount_due=item.amount_due,
            days_overdue=item.days_overdue,
        )
        db.add(rec)
        count += 1
    db.commit()
    return schemas.ReceivableUploadResponse(message="Receivables uploaded", count=count)

@router.get("/{receivable_id}/priority")
def receivable_priority(receivable_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.Receivable).filter(models.Receivable.id == receivable_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Receivable not found")
    # Simple priority: amount * days_overdue
    score = rec.amount_due * rec.days_overdue
    rec.priority_score = score
    db.commit()
    return {"priority_score": score}

@router.get("/{receivable_id}/email", response_model=schemas.EmailDraftResponse)
def receivable_email(receivable_id: int, db: Session = Depends(get_db)):
    rec = db.query(models.Receivable).filter(models.Receivable.id == receivable_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Receivable not found")
    # Generate email using mock or Gemini
    email = email_generator.generate_email(
        customer=rec.customer,
        invoice_number="N/A",
        amount=rec.amount_due,
        due_date=str(datetime.date.today() + datetime.timedelta(days=rec.days_overdue)),
        currency="USD",
    )
    rec.email_draft = email["body"]
    db.commit()
    return schemas.EmailDraftResponse(**email)
