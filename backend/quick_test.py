#!/usr/bin/env python3
import requests

# Test audit log creation and retrieval
login_response = requests.post('http://localhost:8001/api/auth/login', 
                             json={'email': 'test@test.com', 'password': 'password123'})

if login_response.status_code == 200:
    token = login_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create a test audit log
    create_response = requests.post('http://localhost:8001/api/audit/', 
                                  json={
                                      'action': 'Test Activity', 
                                      'details': 'Testing recent activity display',
                                      'status': 'success'
                                  }, 
                                  headers=headers)
    
    print(f'Create: {create_response.status_code}')
    
    # Retrieve audit logs
    audit_response = requests.get('http://localhost:8001/api/audit/', headers=headers)
    print(f'Retrieve: {audit_response.status_code}')
    
    if audit_response.status_code == 200:
        logs = audit_response.json()
        print(f'Found {len(logs)} logs')
        for log in logs:
            print(f'  {log.get("action")}: {log.get("details")}')
else:
    print(f'Login failed: {login_response.status_code}')
