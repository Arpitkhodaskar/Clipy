#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8001"

def debug_audit_flow():
    """Detailed debugging of audit log creation and retrieval"""
    
    # Use the existing user from previous test
    email = "test_debug_1751150970@test.com"
    password = "testpass123"
    
    print(f"Logging in as: {email}")
    
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
    
    # First, check what audit logs exist before creating new ones
    print(f"\n1. Checking existing audit logs...")
    get_response = requests.get(f"{BASE_URL}/api/audit/", headers=headers)
    print(f"   Existing logs status: {get_response.status_code}")
    
    if get_response.status_code == 200:
        existing_logs = get_response.json()
        print(f"   Found {len(existing_logs)} existing logs")
        for i, log in enumerate(existing_logs):
            print(f"     {i+1}. {log.get('action', 'N/A')}: {log.get('details', 'N/A')}")
    else:
        print(f"   Error getting existing logs: {get_response.text}")
    
    # Create a new audit log
    print(f"\n2. Creating new audit log...")
    params = {
        "action": f"debug_test_{int(time.time())}",
        "details": f"Debug audit log created at {datetime.now()}",
        "status": "info",
        "device": "Debug Test Device"
    }
    
    print(f"   Params: {params}")
    create_response = requests.post(f"{BASE_URL}/api/audit/", params=params, headers=headers)
    print(f"   Creation status: {create_response.status_code}")
    
    if create_response.status_code == 200:
        result = create_response.json()
        log_id = result.get("id")
        print(f"   ✅ Created audit log with ID: {log_id}")
    else:
        print(f"   ❌ Creation failed: {create_response.text}")
        return
    
    # Wait a moment for potential eventual consistency
    print(f"\n3. Waiting 2 seconds for potential database sync...")
    time.sleep(2)
    
    # Check audit logs again
    print(f"\n4. Checking audit logs after creation...")
    get_response2 = requests.get(f"{BASE_URL}/api/audit/", headers=headers)
    print(f"   Status: {get_response2.status_code}")
    
    if get_response2.status_code == 200:
        logs_after = get_response2.json()
        print(f"   Found {len(logs_after)} logs after creation")
        for i, log in enumerate(logs_after):
            print(f"     {i+1}. {log.get('action', 'N/A')}: {log.get('details', 'N/A')} (ID: {log.get('id', 'N/A')})")
            
        # Check if our new log is in the results
        new_log_found = any(log.get('id') == log_id for log in logs_after)
        print(f"   New log with ID {log_id} found in results: {new_log_found}")
    else:
        print(f"   Error: {get_response2.text}")
    
    # Test audit stats
    print(f"\n5. Checking audit stats...")
    stats_response = requests.get(f"{BASE_URL}/api/audit/stats", headers=headers)
    print(f"   Stats status: {stats_response.status_code}")
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"   Stats: {json.dumps(stats, indent=4)}")
    else:
        print(f"   Stats error: {stats_response.text}")

if __name__ == "__main__":
    from datetime import datetime
    debug_audit_flow()
