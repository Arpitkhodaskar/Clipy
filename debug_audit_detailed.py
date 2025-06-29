#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def test_audit_creation():
    """Test audit log creation with detailed error reporting"""
    
    # Test data
    audit_data = {
        "user_id": "test_user_123",
        "action": "test_action",
        "details": "Test audit log creation",
        "device_info": "Test Device",
        "ip_address": "127.0.0.1"
    }
    
    print("Testing audit log creation...")
    print(f"Data: {json.dumps(audit_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/audit/",
            json=audit_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 422:
            print("Validation Error Details:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2))
            except:
                print("Could not parse error response as JSON")
                print(f"Raw response: {response.text}")
        elif response.status_code == 200:
            print("Success!")
            print(f"Response: {response.json()}")
        else:
            print(f"Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error making request: {e}")

def test_audit_retrieval():
    """Test audit log retrieval"""
    try:
        response = requests.get(f"{BASE_URL}/api/audit/test_user_123")
        print(f"\nRetrieval Status: {response.status_code}")
        if response.status_code == 200:
            logs = response.json()
            print(f"Found {len(logs)} logs")
            for log in logs:
                print(f"  - {log}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error retrieving: {e}")

if __name__ == "__main__":
    test_audit_creation()
    test_audit_retrieval()
