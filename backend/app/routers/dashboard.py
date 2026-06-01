# backend/app/routers/dashboard.py
import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    # Total invoices
    total_invoices = db.query(models.Invoice).count()
    
    # Total payable amount
    total_payable = db.query(func.sum(models.Invoice.amount)).scalar() or 0.0
    
    # High-priority invoices (score >= 0.8 or 80 depending on scale, let's use >= 0.8 as it's the new scale, but legacy might be > 80. We'll use > 80 for legacy, and > 0.8 for new. Or just >= 0.8)
    high_priority_count = db.query(models.Invoice).filter(models.Invoice.priority_score >= 0.8).count()
    # If using legacy 0-100 scale, adjust. Wait, my code uses `score >= 85` for legacy, and AI uses 0-1. So maybe filter >= 0.8 or >= 80.
    # Actually, let's just do an OR or check > 0.8. Since we dropped the DB, everything is new scale (0-1).
    
    # Potential duplicate invoices
    duplicate_count = db.query(models.Invoice).filter(models.Invoice.duplicate_flag == True).count()
    
    # Due Date logic
    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)
    next_month = today + datetime.timedelta(days=30)
    
    # Due this week (between today and next 7 days)
    due_this_week_count = db.query(models.Invoice).filter(
        models.Invoice.due_date >= today,
        models.Invoice.due_date <= next_week
    ).count()
    
    due_this_week_amount = db.query(func.sum(models.Invoice.amount)).filter(
        models.Invoice.due_date >= today,
        models.Invoice.due_date <= next_week
    ).scalar() or 0.0

    due_this_month_amount = db.query(func.sum(models.Invoice.amount)).filter(
        models.Invoice.due_date >= today,
        models.Invoice.due_date <= next_month
    ).scalar() or 0.0
    
    # Overdue invoices
    overdue_count = db.query(models.Invoice).filter(models.Invoice.due_date < today).count()
    overdue_amount = db.query(func.sum(models.Invoice.amount)).filter(models.Invoice.due_date < today).scalar() or 0.0
    
    return {
        "total_invoices": total_invoices,
        "total_payable": round(total_payable, 2),
        "high_priority_count": high_priority_count,
        "duplicate_count": duplicate_count,
        "due_this_week_count": due_this_week_count,
        "due_this_week_amount": round(due_this_week_amount, 2),
        "due_this_month_amount": round(due_this_month_amount, 2),
        "overdue_count": overdue_count,
        "overdue_amount": round(overdue_amount, 2),
    }

@router.get("/cashflow")
def get_cashflow(db: Session = Depends(get_db)):
    # Group invoice amounts by due date for the next 30 days
    today = datetime.date.today()
    next_month = today + datetime.timedelta(days=30)
    
    results = db.query(
        models.Invoice.due_date,
        func.sum(models.Invoice.amount).label("total")
    ).filter(
        models.Invoice.due_date >= today,
        models.Invoice.due_date <= next_month
    ).group_by(models.Invoice.due_date).order_by(models.Invoice.due_date).all()
    
    # Fill in missing dates with 0
    date_map = {row[0]: row[1] for row in results if row[0]}
    
    data = []
    for i in range(30):
        d = today + datetime.timedelta(days=i)
        data.append({
            "date": d.isoformat(),
            "amount": round(date_map.get(d, 0.0), 2)
        })
        
    return data

@router.get("/vendors")
def get_vendor_analytics(db: Session = Depends(get_db)):
    results = db.query(
        models.Invoice.vendor_name,
        func.count(models.Invoice.id).label("invoice_count"),
        func.sum(models.Invoice.amount).label("total_spend"),
        models.Invoice.vendor_category
    ).group_by(models.Invoice.vendor_name, models.Invoice.vendor_category).all()
    
    vendors = []
    for row in results:
        if row[0]: # Ensure vendor_name exists
            vendors.append({
                "vendor_name": row[0],
                "invoice_count": row[1],
                "total_spend": round(row[2] or 0.0, 2),
                "category": row[3] or "Unknown"
            })
            
    # Also fetch distinct risk notes for each vendor
    # (Doing this in a simple way for SQLite)
    for v in vendors:
        # Get one recent risk note
        recent = db.query(models.Invoice).filter(
            models.Invoice.vendor_name == v["vendor_name"],
            models.Invoice.vendor_reasoning != None
        ).first()
        v["risk_notes"] = recent.vendor_reasoning if recent else ""
        
    return vendors
