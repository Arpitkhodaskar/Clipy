#!/usr/bin/env python3
"""
Simple test to debug shared clipboard API
"""
import requests
import json

def test_simple_shared_clipboard():
    base_url = "http://localhost:8001"
    
    # First register and login a user
    test_user = {
        "email": "debuguser2@example.com",
        "password": "testpass123",
        "name": "Debug User",
        "organization": "Test Org"
    }
    
    print("1. Registering user...")
    register_response = requests.post(
        f"{base_url}/api/auth/register",
        json=test_user,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    print(f"Register status: {register_response.status_code}")
    if register_response.status_code != 200:
        print(f"Register error: {register_response.text}")
    
    print("2. Logging in...")
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        },
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    print(f"Got token: {token[:20]}...")
    
    print("3. Testing test-shared endpoint...")
    test_response = requests.get(
        f"{base_url}/api/clipboard/test-shared",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    print(f"Test-shared status: {test_response.status_code}")
    if test_response.status_code == 200:
        print(f"Test-shared response: {test_response.json()}")
    else:
        print(f"Test-shared error: {test_response.text}")
    
    print("4. Testing regular clipboard fetch...")
    regular_response = requests.get(
        f"{base_url}/api/clipboard/?shared=false",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    print(f"Regular fetch status: {regular_response.status_code}")
    if regular_response.status_code == 200:
        data = regular_response.json()
        print(f"Regular items count: {len(data)}")
    else:
        print(f"Regular fetch error: {regular_response.text}")
    
    print("5. Testing shared clipboard fetch...")
    shared_response = requests.get(
        f"{base_url}/api/clipboard/?shared=true",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    print(f"Shared fetch status: {shared_response.status_code}")
    if shared_response.status_code != 200:
        print(f"Shared fetch error: {shared_response.text}")
        print(f"Response headers: {shared_response.headers}")
        try:
            error_detail = shared_response.json()
            print(f"Error detail: {error_detail}")
        except:
            print("Could not parse error as JSON")
    else:
        data = shared_response.json()
        print(f"Shared items count: {len(data)}")

if __name__ == "__main__":
    test_simple_shared_clipboard()
