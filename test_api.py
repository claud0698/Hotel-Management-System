#!/usr/bin/env python3
"""
Quick API Test Script
Test the deployed backend API
"""

import requests
import json

API_URL = "https://kos-backend-228057609267.asia-southeast1.run.app"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200

def test_login(username="admin", password="admin123"):
    """Test login and get token"""
    print(f"Testing login with {username}...")
    response = requests.post(
        f"{API_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Token received: {data['access_token'][:20]}...")
        print(f"User: {data['user']}\n")
        return data['access_token']
    else:
        print(f"Error: {response.text}\n")
        return None

def test_rooms(token):
    """Test rooms endpoint"""
    print("Testing /api/rooms...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/api/rooms", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {data.keys()}")
        print(f"Total rooms: {data.get('total', 'N/A')}")
        print(f"Rooms count: {len(data.get('rooms', []))}")
        if data.get('rooms'):
            print(f"First room: {json.dumps(data['rooms'][0], indent=2)}")
        else:
            print("No rooms found in database")
    else:
        print(f"Error: {response.text}")
    print()
    return response.status_code == 200

def main():
    print("=" * 60)
    print("API Test Script - Kos Management Backend")
    print("=" * 60 + "\n")

    # Test health
    if not test_health():
        print("❌ Health check failed!")
        return

    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed!")
        print("\nTrying to check if admin user exists...")
        # The admin user might not exist yet
        return

    # Test rooms
    if test_rooms(token):
        print("✅ All tests passed!")
    else:
        print("❌ Rooms endpoint failed!")

if __name__ == "__main__":
    main()
