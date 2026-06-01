import sys
import os

# Ensure backend can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def run_tests():
    print("Testing GET /receivable...")
    resp = client.get("/receivable")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Success! Found {len(data)} receivables.")
        if len(data) > 0:
            print(f"Sample: {data[0]}")
    else:
        print(f"Failed with {resp.status_code}: {resp.text}")

    print("\nTesting POST /receivable/upload...")
    payload = [
        {
            "customer": "Test Customer",
            "amount_due": 1500.0,
            "days_overdue": 12
        }
    ]
    resp = client.post("/receivable/upload", json=payload)
    if resp.status_code == 200:
        print(f"Success! {resp.json()}")
    else:
        print(f"Failed with {resp.status_code}: {resp.text}")

    print("\nTesting GET /receivable/1/email...")
    resp = client.get("/receivable/1/email?reminder_type=Friendly")
    if resp.status_code == 200:
        data = resp.json()
        print("Success! Generated email draft:")
        print(f"Subject: {data.get('subject')}")
        print(f"Body: {data.get('body')}")
    else:
        print(f"Failed with {resp.status_code}: {resp.text}")

if __name__ == "__main__":
    run_tests()
