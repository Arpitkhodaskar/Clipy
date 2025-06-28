#!/usr/bin/env python3
"""
Test device registration during signup flow
"""
import asyncio
import sys
import os
import requests
import json
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

async def test_signup_device_registration():
    """Test that devices are properly registered during user signup"""
    base_url = "http://localhost:8001"
    
    # Test user data
    test_user = {
        "email": f"testdevice_{int(asyncio.get_event_loop().time())}@example.com",
        "password": "testpass123",
        "name": "Test Device User",
        "organization": "Test Org"
    }
    
    print(f"🧪 Testing device registration for new user: {test_user['email']}")
    
    try:
        # 1. Register new user
        print("📝 Step 1: Registering new user...")
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json=test_user,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        if register_response.status_code != 200:
            print(f"❌ Registration failed: {register_response.status_code} - {register_response.text}")
            return False
        
        print(f"✅ User registered successfully")
        
        # 2. Login to get token
        print("🔐 Step 2: Logging in to get access token...")
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            },
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
        
        login_data = login_response.json()
        access_token = login_data.get("access_token")
        
        if not access_token:
            print("❌ No access token received")
            return False
        
        print(f"✅ Login successful, got token")
        
        # 3. Fetch devices for the user
        print("📱 Step 3: Fetching user devices...")
        devices_response = requests.get(
            f"{base_url}/api/devices/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
        )
        
        if devices_response.status_code != 200:
            print(f"❌ Failed to fetch devices: {devices_response.status_code} - {devices_response.text}")
            return False
        
        devices = devices_response.json()
        print(f"📱 Found {len(devices)} devices:")
        for device in devices:
            print(f"  - {device['name']} ({device['device_type']}) - Trusted: {device['is_trusted']}")
        
        # 4. Fetch device stats (optional since frontend now calculates from devices)
        print("📊 Step 4: Fetching device stats...")
        try:
            stats_response = requests.get(
                f"{base_url}/api/devices/stats",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"📊 Device stats: {json.dumps(stats, indent=2)}")
            else:
                print(f"⚠️ Stats endpoint not available (but frontend can calculate from devices): {stats_response.status_code}")
                # Calculate stats from devices (same as frontend now does)
                stats = {
                    "total": len(devices),
                    "online": sum(1 for d in devices if d.get("is_online", False)),
                    "trusted": sum(1 for d in devices if d.get("is_trusted", False)),
                    "pending": sum(1 for d in devices if not d.get("is_trusted", False))
                }
                print(f"📊 Calculated device stats: {json.dumps(stats, indent=2)}")
        except Exception as e:
            print(f"⚠️ Stats endpoint error (but devices are working): {e}")
            stats = {
                "total": len(devices),
                "online": sum(1 for d in devices if d.get("is_online", False)),
                "trusted": sum(1 for d in devices if d.get("is_trusted", False)),
                "pending": sum(1 for d in devices if not d.get("is_trusted", False))
            }
            print(f"📊 Calculated device stats: {json.dumps(stats, indent=2)}")
        
        # Validate that at least one device was registered during signup
        if len(devices) == 0:
            print("❌ ISSUE FOUND: No devices were registered during signup!")
            return False
        
        # Calculate stats if they weren't available from API
        if 'stats' not in locals():
            stats = {
                "total": len(devices),
                "online": sum(1 for d in devices if d.get("is_online", False)),
                "trusted": sum(1 for d in devices if d.get("is_trusted", False)),
                "pending": sum(1 for d in devices if not d.get("is_trusted", False))
            }
        
        if stats.get("total", 0) == 0:
            print("❌ ISSUE FOUND: Device stats show 0 total devices!")
            return False
        
        print("✅ SUCCESS: Device was properly registered during signup!")
        print(f"✅ Device details: {devices[0]['name']} - {devices[0]['device_type']} - Trusted: {devices[0]['is_trusted']}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_signup_device_registration())
    sys.exit(0 if result else 1)
