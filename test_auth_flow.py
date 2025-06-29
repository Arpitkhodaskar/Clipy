#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_registration_response():
    """Check what the registration endpoint actually returns"""
    
    email = f"test_debug_{int(time.time())}@test.com"
    password = "testpass123"
    
    register_data = {
        "email": email,
        "name": "Test Debug User",
        "password": password,
        "organization": "Test Org"
    }
    
    print(f"Testing registration response for: {email}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("Registration response:")
            print(json.dumps(result, indent=2))
            
            # Try to login to get token
            print(f"\nNow trying to login...")
            login_data = {"email": email, "password": password}
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            print(f"Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("Login response:")
                print(json.dumps(login_result, indent=2))
                return login_result.get("access_token")
            else:
                print(f"Login failed: {login_response.text}")
                
        else:
            print(f"Registration failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    token = test_registration_response()
    if token:
        print(f"\n✅ Got token: {token[:50]}...")
    else:
        print(f"\n❌ No token obtained")
