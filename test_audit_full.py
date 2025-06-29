#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def register_and_get_token():
    """Register a test user and get authentication token"""
    # Generate unique email
    import time
    email = f"test_audit_{int(time.time())}@test.com"
    password = "testpass123"
    
    print(f"Registering user: {email}")
    
    # Register user
    register_data = {
        "email": email,
        "name": "Test Audit User",
        "password": password,
        "organization": "Test Org"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            user_id = result.get("id")
            print(f"✅ Registered successfully. User ID: {user_id}")
            
            # Now login to get token
            print(f"Logging in to get token...")
            login_data = {"email": email, "password": password}
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                token = login_result.get("access_token")
                print(f"✅ Login successful, got token")
                return token, user_id, email
            else:
                print(f"❌ Login failed: {login_response.text}")
                return None, None, None
        else:
            print(f"Registration failed: {response.text}")
            return None, None, None
            
    except Exception as e:
        print(f"Registration error: {e}")
        return None, None, None

def test_audit_with_valid_token():
    """Test audit log creation with valid authentication"""
    token, user_id, email = register_and_get_token()
    
    if not token:
        print("❌ Could not get valid token, skipping audit test")
        return
    
    # Test audit log creation
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "action": "test_login",
        "details": f"Test audit log for user {email}",
        "status": "success",
        "device": "Test Device"
    }
    
    print(f"\nCreating audit log with valid token...")
    print(f"Params: {params}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/audit/", params=params, headers=headers)
        print(f"Audit creation status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Audit log created successfully!")
            print(f"Response: {response.json()}")
            
            # Now test retrieval
            print(f"\nRetrieving audit logs for user...")
            get_response = requests.get(f"{BASE_URL}/api/audit/", headers=headers)
            print(f"Retrieval status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                logs = get_response.json()
                print(f"✅ Found {len(logs)} audit logs:")
                for log in logs:
                    print(f"  - {log.get('action', 'N/A')}: {log.get('details', 'N/A')} ({log.get('timestamp', 'N/A')})")
            else:
                print(f"❌ Retrieval failed: {get_response.text}")
        else:
            print(f"❌ Audit creation failed: {response.text}")
            
    except Exception as e:
        print(f"Error testing audit: {e}")

if __name__ == "__main__":
    test_audit_with_valid_token()
