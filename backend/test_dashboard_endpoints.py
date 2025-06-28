#!/usr/bin/env python3
"""
Test dashboard API endpoints
"""
import requests
import json

def test_dashboard_endpoints():
    base_url = "http://localhost:8001"
    
    # Login to get a token
    test_user = {
        "email": "debuguser2@example.com",
        "password": "testpass123"
    }
    
    print("🔐 Logging in...")
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json=test_user,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get("access_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test device stats
    print("\n📱 Testing device stats...")
    device_response = requests.get(f"{base_url}/api/devices/stats", headers=headers)
    print(f"Device stats status: {device_response.status_code}")
    if device_response.status_code == 200:
        print(f"Device stats: {device_response.json()}")
    else:
        print(f"Device stats error: {device_response.text}")
    
    # Test audit stats
    print("\n📊 Testing audit stats...")
    audit_response = requests.get(f"{base_url}/api/audit/stats", headers=headers)
    print(f"Audit stats status: {audit_response.status_code}")
    if audit_response.status_code == 200:
        print(f"Audit stats: {audit_response.json()}")
    else:
        print(f"Audit stats error: {audit_response.text}")
    
    # Test clipboard stats
    print("\n📋 Testing clipboard stats...")
    clipboard_response = requests.get(f"{base_url}/api/clipboard/stats", headers=headers)
    print(f"Clipboard stats status: {clipboard_response.status_code}")
    if clipboard_response.status_code == 200:
        print(f"Clipboard stats: {clipboard_response.json()}")
    else:
        print(f"Clipboard stats error: {clipboard_response.text}")

if __name__ == "__main__":
    test_dashboard_endpoints()
