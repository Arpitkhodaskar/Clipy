#!/usr/bin/env python3
import requests
import json

def create_demo_user():
    """Create a demo user for easy login"""
    
    BASE_URL = "http://localhost:8001"
    
    print("=== CREATING DEMO USER ===\n")
    
    # Demo user data
    demo_data = {
        "email": "demo@clipvault.com",
        "name": "Demo User",
        "password": "demopassword",
        "organization": "ClipVault Demo"
    }
    
    print(f"Creating demo user: {demo_data['email']}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=demo_data)
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Demo user created successfully!")
            print(f"User ID: {result.get('id')}")
            print(f"Name: {result.get('name')}")
            print(f"Email: {result.get('email')}")
            
            # Now test login
            print(f"\n🔑 Testing demo user login...")
            login_data = {
                "email": demo_data["email"],
                "password": demo_data["password"]
            }
            
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            print(f"Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Demo user login successful!")
                print(f"Token: {login_result.get('access_token', 'N/A')[:50]}...")
                return True
            else:
                print(f"❌ Demo user login failed: {login_response.text}")
                
        elif response.status_code == 400 and "already registered" in response.text:
            print("✅ Demo user already exists!")
            
            # Test login
            print(f"\n🔑 Testing existing demo user login...")
            login_data = {
                "email": demo_data["email"],
                "password": demo_data["password"]
            }
            
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
            print(f"Login status: {login_response.status_code}")
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                print("✅ Demo user login successful!")
                print(f"Token: {login_result.get('access_token', 'N/A')[:50]}...")
                return True
            else:
                print(f"❌ Demo user login failed: {login_response.text}")
        else:
            print(f"❌ Demo user creation failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
    
    return False

if __name__ == "__main__":
    success = create_demo_user()
    
    if success:
        print("\n✅ Demo user is ready!")
        print("You can now login with:")
        print("  Email: demo@clipvault.com")
        print("  Password: demopassword")
    else:
        print("\n❌ Demo user setup failed")
        print("You can use one of these existing users:")
        print("  Email: test_debug_1751150970@test.com")
        print("  Password: testpass123")
