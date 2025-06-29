#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_simple_audit_retrieval():
    """Test audit retrieval with existing user"""
    
    # Use the existing user
    email = "test_debug_1751150970@test.com"
    password = "testpass123"
    
    # Login to get token
    login_data = {"email": email, "password": password}
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result.get("access_token")
    print(f"✅ Login successful")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different variations of the GET request
    print(f"\n1. Testing basic GET /api/audit/")
    response1 = requests.get(f"{BASE_URL}/api/audit/", headers=headers)
    print(f"   Status: {response1.status_code}")
    print(f"   Response: {response1.text}")
    
    print(f"\n2. Testing GET with limit parameter")
    response2 = requests.get(f"{BASE_URL}/api/audit/?limit=10", headers=headers)
    print(f"   Status: {response2.status_code}")
    print(f"   Response: {response2.text}")
    
    print(f"\n3. Testing GET with no ordering")
    response3 = requests.get(f"{BASE_URL}/api/audit/?limit=5&offset=0", headers=headers)
    print(f"   Status: {response3.status_code}")
    print(f"   Response: {response3.text}")

if __name__ == "__main__":
    test_simple_audit_retrieval()
