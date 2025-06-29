#!/usr/bin/env python3
import requests
import json

def test_login_endpoint():
    """Test login endpoint connectivity and functionality"""
    
    BASE_URL = "http://localhost:8001"
    
    print("=== LOGIN ENDPOINT TEST ===\n")
    
    # Test 1: Check if backend is responding
    print("1. 🌐 Testing backend connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Backend status: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Backend is responding (404 expected for root)")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Backend not reachable: {e}")
        return False
    
    # Test 2: Try login with demo credentials
    print("\n2. 🔑 Testing login with demo credentials...")
    login_data = {
        "email": "demo@clipvault.com",
        "password": "demopassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Login successful!")
            print(f"   Token received: {result.get('access_token', 'N/A')[:50]}...")
            return True
        else:
            print(f"   ❌ Login failed: {response.text}")
            
            # Try with the test user we know exists
            print("\n   🔄 Trying with known test user...")
            test_login_data = {
                "email": "test_debug_1751150970@test.com",
                "password": "testpass123"
            }
            
            test_response = requests.post(f"{BASE_URL}/api/auth/login", json=test_login_data)
            print(f"   Test user login status: {test_response.status_code}")
            
            if test_response.status_code == 200:
                test_result = test_response.json()
                print("   ✅ Test user login successful!")
                print(f"   Token: {test_result.get('access_token', 'N/A')[:50]}...")
                return True
            else:
                print(f"   ❌ Test user login also failed: {test_response.text}")
                
    except Exception as e:
        print(f"   ❌ Login request failed: {e}")
    
    # Test 3: Check CORS
    print("\n3. 🌍 Testing CORS headers...")
    try:
        response = requests.options(f"{BASE_URL}/api/auth/login")
        headers = dict(response.headers)
        cors_headers = {k: v for k, v in headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print("   ✅ CORS headers present:")
            for k, v in cors_headers.items():
                print(f"     {k}: {v}")
        else:
            print("   ⚠️ No CORS headers found")
    except Exception as e:
        print(f"   ❌ CORS test failed: {e}")
    
    return False

if __name__ == "__main__":
    success = test_login_endpoint()
    
    if not success:
        print("\n🔧 TROUBLESHOOTING STEPS:")
        print("1. Check if backend server is running on port 8001")
        print("2. Verify CORS settings in backend")
        print("3. Check browser console for specific error details")
        print("4. Try refreshing the page or clearing browser cache")
    else:
        print("\n✅ Login endpoint is working properly!")
