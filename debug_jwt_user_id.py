#!/usr/bin/env python3
import requests
import json
import jwt
import time

BASE_URL = "http://localhost:8001"

def decode_jwt_and_debug():
    """Debug JWT token and user ID extraction"""
    
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
    print(f"✅ Got token: {token}")
    
    # Decode JWT token (without verification for debugging)
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"\nJWT payload:")
        print(json.dumps(decoded, indent=2))
        
        user_id_from_jwt = decoded.get("sub")
        print(f"\nUser ID from JWT: {user_id_from_jwt}")
        
        # Now create an audit log and manually check Firestore
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "action": "jwt_debug_test",
            "details": f"Testing user ID {user_id_from_jwt}",
            "status": "info"
        }
        
        print(f"\nCreating audit log with JWT user ID: {user_id_from_jwt}")
        create_response = requests.post(f"{BASE_URL}/api/audit/", params=params, headers=headers)
        
        if create_response.status_code == 200:
            result = create_response.json()
            log_id = result.get("id")
            print(f"✅ Created audit log with ID: {log_id}")
            
            # Now try to query by the specific user ID
            print(f"\nTrying to retrieve logs for user: {user_id_from_jwt}")
            get_response = requests.get(f"{BASE_URL}/api/audit/", headers=headers)
            
            if get_response.status_code == 200:
                logs = get_response.json()
                print(f"Found {len(logs)} logs")
                if logs:
                    for log in logs:
                        print(f"  Log: {log}")
                else:
                    print("No logs returned despite successful creation")
            else:
                print(f"Error retrieving logs: {get_response.text}")
        else:
            print(f"❌ Failed to create audit log: {create_response.text}")
            
    except Exception as e:
        print(f"Error decoding JWT: {e}")

if __name__ == "__main__":
    decode_jwt_and_debug()
