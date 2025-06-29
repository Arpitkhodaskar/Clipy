#!/usr/bin/env python3
"""
Test audit logs API endpoint
"""

import requests
import json

def test_audit_api():
    # First login to get a token
    login_data = {
        'email': 'test@test.com',
        'password': 'password123'
    }

    print('🔑 Logging in to get token...')
    login_response = requests.post('http://localhost:8001/api/auth/login', json=login_data)
    print(f'Login status: {login_response.status_code}')

    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        print('📜 Testing audit logs endpoint...')
        audit_response = requests.get('http://localhost:8001/api/audit/', headers=headers)
        print(f'Audit logs status: {audit_response.status_code}')
        
        if audit_response.status_code == 200:
            logs = audit_response.json()
            print(f'Found {len(logs)} audit logs')
            for log in logs[:5]:
                print(f'  - {log.get("action", "N/A")}: {log.get("details", "N/A")} at {log.get("timestamp", "N/A")}')
        else:
            print(f'Error response: {audit_response.text}')
            
        print('📊 Testing audit stats endpoint...')
        stats_response = requests.get('http://localhost:8001/api/audit/stats', headers=headers)
        print(f'Stats status: {stats_response.status_code}')
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f'Stats: {json.dumps(stats, indent=2)}')
        else:
            print(f'Stats error: {stats_response.text}')
    else:
        print(f'Login failed: {login_response.text}')

if __name__ == '__main__':
    test_audit_api()
