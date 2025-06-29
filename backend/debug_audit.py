#!/usr/bin/env python3
"""
Test to check if ANY audit logs exist in Firebase
"""

import requests
import json
import time

def check_all_audit_logs():
    # Login first to get a token
    login_response = requests.post('http://localhost:8001/api/auth/login', 
                                 json={'email': 'test@test.com', 'password': 'password123'})
    
    if login_response.status_code == 200:
        token = login_response.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Try different endpoints to debug
        print('🔍 Testing audit endpoints...')
        
        # Test stats endpoint
        stats_response = requests.get('http://localhost:8001/api/audit/stats', headers=headers)
        print(f'Stats status: {stats_response.status_code}')
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f'Stats data: {json.dumps(stats, indent=2)}')
        else:
            print(f'Stats error: {stats_response.text}')
        
        # Test main audit endpoint
        audit_response = requests.get('http://localhost:8001/api/audit/', headers=headers)
        print(f'Audit status: {audit_response.status_code}')
        if audit_response.status_code == 200:
            logs = audit_response.json()
            print(f'Audit logs count: {len(logs)}')
        else:
            print(f'Audit error: {audit_response.text}')
    else:
        print(f'Login failed: {login_response.text}')

if __name__ == '__main__':
    check_all_audit_logs()
