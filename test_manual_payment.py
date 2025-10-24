#!/usr/bin/env python3
"""
Test script for manual payment endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Test data
TENANT_ID = 1  # Assuming tenant 1 exists from seeding
PAYMENT_DATA = {
    "tenant_id": TENANT_ID,
    "period_months": 2,
    "status": "pending",
    "payment_method": "cash",
    "notes": "Payment for 2 months stay"
}

def test_manual_payment():
    """Test the manual payment creation endpoint"""
    print("=" * 60)
    print("Testing Manual Payment Creation Endpoint")
    print("=" * 60)

    url = f"{BASE_URL}/payments/manual/create"

    print(f"\nEndpoint: POST {url}")
    print(f"\nRequest body:")
    print(json.dumps(PAYMENT_DATA, indent=2))

    try:
        response = requests.post(url, json=PAYMENT_DATA)

        print(f"\nResponse Status: {response.status_code}")
        print(f"\nResponse Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 201:
            print("\n✓ SUCCESS: Payment created!")
            payment = response.json().get('payment', {})
            details = response.json().get('details', {})
            print(f"\n  - Payment ID: {payment.get('id')}")
            print(f"  - Tenant: {details.get('tenant_name')}")
            print(f"  - Room: {details.get('room_number')}")
            print(f"  - Monthly Rate: {details.get('monthly_rate'):,.0f}")
            print(f"  - Period: {details.get('period_months')} months")
            print(f"  - Total Amount: {details.get('total_amount'):,.0f}")
            print(f"  - Due Date: {details.get('due_date')}")
            print(f"  - Status: {payment.get('status')}")
        else:
            print("\n✗ FAILED: Something went wrong")

    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")

def test_get_payments():
    """Get all payments to verify the new one was created"""
    print("\n" + "=" * 60)
    print("Fetching All Payments")
    print("=" * 60)

    url = f"{BASE_URL}/payments"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            payments = response.json().get('payments', [])
            print(f"\nTotal payments: {len(payments)}")

            # Show last 3 payments
            print("\nLast 3 payments:")
            for payment in payments[-3:]:
                print(f"\n  ID: {payment['id']}")
                print(f"  Tenant ID: {payment['tenant_id']}")
                print(f"  Amount: {payment['amount']:,.0f}")
                print(f"  Period: {payment.get('period_months', 1)} month(s)")
                print(f"  Due Date: {payment['due_date']}")
                print(f"  Status: {payment['status']}")
        else:
            print(f"✗ FAILED: Status {response.status_code}")
            print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")

if __name__ == "__main__":
    print("\n")
    print("Make sure the backend is running with: uvicorn app:app --reload")
    print("Also make sure the database is seeded with: python seed.py")
    print("\n")

    test_manual_payment()
    test_get_payments()

    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60 + "\n")
