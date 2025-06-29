#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_audit_creation_correct():
    """Test audit log creation with correct query parameters"""
    
    # Test with query parameters instead of JSON body
    params = {
        "action": "test_action", 
        "details": "Test audit log creation",
        "status": "success",
        "device": "Test Device"
    }
    
    # Create a fake JWT token for testing (or use auth header)
    headers = {
        "Authorization": "Bearer fake-token-for-testing"
    }
    
    print("Testing audit log creation with query parameters...")
    print(f"Params: {params}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/audit/",
            params=params,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print("Validation Error Details:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2))
            except:
                print("Could not parse error response as JSON")
                print(f"Raw response: {response.text}")
        elif response.status_code == 401:
            print("Authentication required - this is expected with fake token")
            print(f"Response: {response.text}")
        elif response.status_code == 200:
            print("Success!")
            print(f"Response: {response.json()}")
        else:
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

def test_without_auth():
    """Test without authentication to see the specific error"""
    params = {
        "action": "test_action",
        "details": "Test without auth" 
    }
    
    print("\nTesting without authentication...")
    try:
        response = requests.post(f"{BASE_URL}/api/audit/", params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_audit_creation_correct()
    test_without_auth()
