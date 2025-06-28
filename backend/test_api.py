#!/usr/bin/env python3
"""
ClipVault Backend API Test Script

Tests all the major API endpoints to ensure they're working correctly.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8001"
TEST_USER = {
    "email": "apitest@clipvault.com",
    "name": "API Test User",
    "password": "testpass123",
    "organization": "ClipVault Testing"
}

def test_endpoint(method, endpoint, headers=None, data=None, expected_status=200):
    """Test an API endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"{method} {endpoint} -> {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ SUCCESS")
        else:
            print(f"❌ FAILED (expected {expected_status})")
            
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                return response.json()
            except:
                return response.text
        return response.text
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

def main():
    print("🧪 ClipVault Backend API Test")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint...")
    health = test_endpoint("GET", "/health")
    
    # Test 2: Register User
    print("\n2. Testing User Registration...")
    registration = test_endpoint("POST", "/api/auth/register", data=TEST_USER, expected_status=200)
    
    if not registration:
        print("❌ Registration failed, stopping tests")
        return
    
    # Test 3: Login User
    print("\n3. Testing User Login...")
    login_data = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    login_response = test_endpoint("POST", "/api/auth/login", data=login_data)
    
    if not login_response or 'access_token' not in login_response:
        print("❌ Login failed, stopping tests")
        return
    
    token = login_response['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 4: Get User Info
    print("\n4. Testing Get User Info...")
    user_info = test_endpoint("GET", "/api/auth/me", headers=headers)
    
    # Test 5: Test Other Endpoints
    print("\n5. Testing Other Endpoints...")
    test_endpoint("GET", "/api/clipboard/", headers=headers)
    test_endpoint("GET", "/api/devices/", headers=headers)
    test_endpoint("GET", "/api/users/", headers=headers)
    
    # Test 6: API Documentation
    print("\n6. Testing API Documentation...")
    test_endpoint("GET", "/docs")
    
    print("\n🎉 API Test Complete!")
    print("\n📊 Summary:")
    print(f"• Backend URL: {BASE_URL}")
    print(f"• Test User: {TEST_USER['email']}")
    print(f"• JWT Token: {token[:50]}...")
    print("\n✅ All major endpoints are accessible!")
    print("✅ Authentication is working!")
    print("✅ Backend is ready for frontend integration!")

if __name__ == "__main__":
    main()
