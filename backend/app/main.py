# backend/app/main.py
"""FastAPI application entry point.
Includes CORS middleware and registers the invoice and receivable routers.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import invoice, receivable, dashboard
from .database import engine, Base
from . import models

# Create tables at startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Operations Copilot API", version="0.1.0")

# Allow all origins for demo purposes; adjust for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(invoice.router, prefix="/invoice", tags=["Invoice"])
app.include_router(receivable.router, prefix="/receivable", tags=["Receivable"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
