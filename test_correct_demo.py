#!/usr/bin/env python3
import requests
import json

def test_correct_demo_login():
    """Test login with the correct demo password"""
    
    BASE_URL = "http://localhost:8001"
    
    print("=== TESTING CORRECT DEMO LOGIN ===\n")
    
    # Test with correct demo password
    login_data = {
        "email": "demo@clipvault.com",
        "password": "demo123"  # Correct password from auth.py
    }
    
    print(f"Testing login with: {login_data['email']} / {login_data['password']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Demo login successful!")
            print(f"Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"Token type: {result.get('token_type', 'N/A')}")
            return True
        else:
            print(f"❌ Demo login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_correct_demo_login()
    
    if success:
        print("\n✅ Demo login works with correct password!")
        print("Frontend should use:")
        print("  Email: demo@clipvault.com") 
        print("  Password: demo123")
    else:
        print("\n❌ Demo login still failing")
