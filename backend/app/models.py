# backend/app/models.py
"""SQLAlchemy ORM models for the Finance Copilot backend.
SQLite is used for simplicity. The tables store raw uploaded data as well as AI‑derived fields.
"""
from sqlalchemy import Column, Integer, String, Float, Date, Boolean
from .database import Base

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    invoice_number = Column(String, nullable=True)
    vendor_name = Column(String, nullable=True)
    invoice_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    vendor_category = Column(String, nullable=True)
    vendor_reasoning = Column(String, nullable=True)
    priority_score = Column(Float, nullable=True)
    duplicate_flag = Column(Boolean, default=False)

class Receivable(Base):
    __tablename__ = "receivables"
    id = Column(Integer, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    amount_due = Column(Float, nullable=False)
    days_overdue = Column(Integer, nullable=False)
    priority_score = Column(Float, nullable=True)
    email_draft = Column(String, nullable=True)
