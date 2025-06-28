#!/usr/bin/env python3
"""
Test script to verify login flow is working
"""

import requests
import json

def test_auth_flow():
    print('🧪 Testing complete auth flow...')

    # Test registration
    register_data = {
        'email': 'test_login_fix@example.com',
        'name': 'Test User',
        'password': 'testpassword123'
    }

    print('1. Testing registration...')
    try:
        reg_response = requests.post('http://localhost:8001/api/auth/register', json=register_data)
        print(f'Registration status: {reg_response.status_code}')

        if reg_response.status_code == 200:
            print('✅ Registration successful')
            
            # Test login
            login_data = {
                'email': 'test_login_fix@example.com',
                'password': 'testpassword123'
            }
            
            print('2. Testing login...')
            login_response = requests.post('http://localhost:8001/api/auth/login', json=login_data)
            print(f'Login status: {login_response.status_code}')
            
            if login_response.status_code == 200:
                print('✅ Login successful')
                token_data = login_response.json()
                token = token_data.get('access_token', '')
                print(f'Received token: {token[:20]}...')
                return True
            else:
                print(f'❌ Login failed: {login_response.text}')
                return False
        else:
            print(f'❌ Registration failed: {reg_response.text}')
            return False
    except Exception as e:
        print(f'❌ Connection error: {e}')
        return False

if __name__ == '__main__':
    test_auth_flow()
