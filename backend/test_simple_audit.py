#!/usr/bin/env python3
"""
Simple test to check Firebase audit logs directly
"""

import requests
import json

def simple_test():
    try:
        print('🆕 Testing new user registration...')
        
        # Register a new user first
        import time
        test_email = f"testuser{int(time.time())}@example.com"
        
        reg_response = requests.post('http://localhost:8001/api/auth/register', 
                                   json={
                                       'email': test_email,
                                       'name': 'Test User',
                                       'password': 'testpass123'
                                   }, timeout=10)
        
        print(f'Registration response status: {reg_response.status_code}')
        
        if reg_response.status_code == 200:
            print('✅ Registration successful')
            
            # Now login with the new user
            print('🔑 Testing login with new user...')
            
            login_response = requests.post('http://localhost:8001/api/auth/login', 
                                         json={'email': test_email, 'password': 'testpass123'},
                                         timeout=10)
            
            print(f'Login response status: {login_response.status_code}')
            
            if login_response.status_code == 200:
                print('✅ Login successful')
                token_data = login_response.json()
                token = token_data.get('access_token', '')
                print(f'Got token: {token[:20]}...')
                
                headers = {'Authorization': f'Bearer {token}'}
                
                # Try to get audit logs
                print('� Fetching audit logs...')
                audit_response = requests.get('http://localhost:8001/api/audit/', 
                                            headers=headers, timeout=10)
                
                print(f'Audit response status: {audit_response.status_code}')
                
                if audit_response.status_code == 200:
                    logs = audit_response.json()
                    print(f'✅ Got {len(logs)} audit logs')
                    
                    if logs:
                        print('📋 Recent logs:')
                        for i, log in enumerate(logs[:5]):
                            print(f'  {i+1}. {log.get("action", "N/A")} - {log.get("details", "N/A")}')
                    else:
                        print('ℹ️ No audit logs found')
                else:
                    print(f'❌ Audit request failed: {audit_response.text}')
            else:
                print(f'❌ Login failed: {login_response.text}')
        else:
            print(f'❌ Registration failed: {reg_response.text}')
        
        # Also test demo user
        print('\\n�🔑 Testing demo login...')
        
        # Login with demo user
        login_response = requests.post('http://localhost:8001/api/auth/login', 
                                     json={'email': 'test@test.com', 'password': 'password123'},
                                     timeout=10)
        
        print(f'Demo login response status: {login_response.status_code}')
        
        if login_response.status_code == 200:
            print('✅ Demo login successful')
            token_data = login_response.json()
            token = token_data.get('access_token', '')
            print(f'Got demo token: {token[:20]}...')
            
            headers = {'Authorization': f'Bearer {token}'}
            
            # Try to get audit logs
            print('📜 Fetching demo audit logs...')
            audit_response = requests.get('http://localhost:8001/api/audit/', 
                                        headers=headers, timeout=10)
            
            print(f'Demo audit response status: {audit_response.status_code}')
            
            if audit_response.status_code == 200:
                logs = audit_response.json()
                print(f'✅ Got {len(logs)} demo audit logs')
                
                if logs:
                    print('📋 Demo recent logs:')
                    for i, log in enumerate(logs[:3]):
                        print(f'  {i+1}. {log.get("action", "N/A")} - {log.get("details", "N/A")}')
                else:
                    print('ℹ️ No demo audit logs found')
            else:
                print(f'❌ Demo audit request failed: {audit_response.text}')
        else:
            print(f'❌ Demo login failed: {login_response.text}')
            
    except requests.exceptions.RequestException as e:
        print(f'❌ Request error: {e}')
    except Exception as e:
        print(f'❌ Unexpected error: {e}')

if __name__ == '__main__':
    simple_test()
