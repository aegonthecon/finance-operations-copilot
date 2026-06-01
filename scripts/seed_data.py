import sys
import os
import random
import datetime

# Add the parent directory to sys.path so we can import the backend package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.database import SessionLocal, engine, Base
from backend.app import models

# Ensure tables exist
Base.metadata.create_all(bind=engine)

def seed_data():
    db = SessionLocal()
    
    # Clear existing data
    db.query(models.Invoice).delete()
    db.query(models.Receivable).delete()
    
    # Seed Invoices
    vendors = [
        ("AWS", "Software", "Standard hosting fees"),
        ("Google Cloud", "Software", "Cloud infrastructure"),
        ("Apoorva Delicacies", "Meals & Entertainment", "Team lunch"),
        ("WeWork", "Infrastructure", "Office space"),
        ("FedEx", "Logistics", "Shipping services"),
        ("Stripe", "Software", "Payment processing fees"),
        ("Salesforce", "Software", "CRM subscription"),
        ("Delta Airlines", "Travel", "Sales team travel"),
    ]
    
    today = datetime.date.today()
    
    print("Seeding Invoices...")
    for i in range(25):
        vendor_name, category, reasoning = random.choice(vendors)
        
        # Mix of overdue, due soon, and upcoming
        days_offset = random.randint(-15, 30)
        due_date = today + datetime.timedelta(days=days_offset)
        invoice_date = due_date - datetime.timedelta(days=30)
        
        amount = round(random.uniform(50, 15000), 2)
        
        # Priority logic mockup for seed data
        priority_score = min(1.0, (amount / 15000.0) * 0.5 + (0.5 if days_offset < 7 else 0.1))
        
        duplicate_risk = random.choice([0.1, 0.1, 0.1, 0.8])
        duplicate_flag = duplicate_risk > 0.5
        
        invoice = models.Invoice(
            file_path=f"mock_data/invoice_{i}.pdf",
            invoice_number=f"INV-{random.randint(1000, 9999)}",
            vendor_name=vendor_name,
            invoice_date=invoice_date,
            due_date=due_date,
            amount=amount,
            currency="USD",
            vendor_category=category,
            vendor_reasoning=reasoning,
            priority_score=priority_score,
            priority_reasoning="High amount and due soon" if priority_score > 0.8 else "Standard priority",
            duplicate_flag=duplicate_flag,
            duplicate_risk=duplicate_risk,
            duplicate_reasoning="Matches another recent invoice" if duplicate_flag else "No duplicates found",
            recommended_action="Review immediately" if duplicate_flag else "Schedule for payment"
        )
        db.add(invoice)
        
    # Seed Receivables
    customers = [
        "Acme Corp", "Globex", "Initech", "Umbrella Corp", "Stark Industries",
        "Wayne Enterprises", "Cyberdyne Systems", "Massive Dynamic"
    ]
    
    print("Seeding Receivables...")
    for i in range(20):
        days_overdue = random.randint(-10, 60)
        risk = "High" if days_overdue > 30 else ("Medium" if days_overdue > 10 else "Low")
        
        rec = models.Receivable(
            customer=random.choice(customers),
            amount_due=round(random.uniform(500, 25000), 2),
            days_overdue=days_overdue,
            customer_risk=risk,
            follow_up_recommendation="Final Notice" if risk == "High" else ("Call Customer" if risk == "Medium" else "Friendly Reminder")
        )
        rec.priority_score = min(rec.amount_due * max(1, rec.days_overdue) / 25000.0, 1.0)
        db.add(rec)
        
    db.commit()
    db.close()
    print("Database seeded successfully with realistic mock data!")

if __name__ == "__main__":
    seed_data()
