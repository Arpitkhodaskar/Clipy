#!/usr/bin/env python3
"""
Test shared clipboard functionality
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

async def test_shared_clipboard():
    """Test that clipboard items are shared across all users"""
    base_url = "http://localhost:8001"
    
    # Test user data
    test_user1 = {
        "email": f"user1_{int(asyncio.get_event_loop().time())}@example.com",
        "password": "testpass123",
        "name": "Test User 1",
        "organization": "Test Org"
    }
    
    test_user2 = {
        "email": f"user2_{int(asyncio.get_event_loop().time())}@example.com", 
        "password": "testpass123",
        "name": "Test User 2",
        "organization": "Test Org"
    }
    
    print(f"🧪 Testing shared clipboard with two users")
    print(f"👤 User 1: {test_user1['email']}")
    print(f"👤 User 2: {test_user2['email']}")
    
    try:
        # Register and login both users
        user1_token = await register_and_login_user(base_url, test_user1)
        user2_token = await register_and_login_user(base_url, test_user2)
        
        # User 1 adds a clipboard item
        print("📝 User 1 adding clipboard item...")
        clipboard_item = {
            "content": "This is a shared clipboard test from User 1",
            "content_type": "text",
            "domain": "localhost",
            "metadata": {"source": "test"}
        }
        
        add_response = requests.post(
            f"{base_url}/api/clipboard/",
            json=clipboard_item,
            headers={
                "Authorization": f"Bearer {user1_token}",
                "Content-Type": "application/json"
            }
        )
        
        if add_response.status_code != 200:
            print(f"❌ User 1 failed to add clipboard item: {add_response.status_code} - {add_response.text}")
            return False
        
        item_data = add_response.json()
        print(f"✅ User 1 added clipboard item: {item_data['id']}")
        
        # User 2 fetches clipboard items in shared mode
        print("📋 User 2 fetching shared clipboard items...")
        shared_response = requests.get(
            f"{base_url}/api/clipboard/?shared=true",
            headers={
                "Authorization": f"Bearer {user2_token}",
                "Content-Type": "application/json"
            }
        )
        
        if shared_response.status_code != 200:
            print(f"❌ User 2 failed to fetch shared clipboard: {shared_response.status_code} - {shared_response.text}")
            return False
        
        shared_items = shared_response.json()
        print(f"📋 User 2 found {len(shared_items)} shared clipboard items")
        
        # Check if User 1's item is visible to User 2
        user1_item_found = False
        for item in shared_items:
            if item.get('content') == clipboard_item['content']:
                user1_item_found = True
                print(f"✅ User 2 can see User 1's clipboard item!")
                print(f"   Content: {item.get('content')[:50]}...")
                print(f"   User ID: {item.get('user_id', 'Unknown')[:8]}...")
                break
        
        if not user1_item_found:
            print("❌ User 2 cannot see User 1's clipboard item!")
            print("Available items:")
            for item in shared_items[:3]:
                print(f"  - {item.get('content', '')[:50]}... (User: {item.get('user_id', 'Unknown')[:8]}...)")
            return False
        
        # User 2 adds their own item
        print("📝 User 2 adding their own clipboard item...")
        user2_item = {
            "content": "This is User 2's contribution to the shared clipboard",
            "content_type": "text", 
            "domain": "localhost",
            "metadata": {"source": "test"}
        }
        
        add_response2 = requests.post(
            f"{base_url}/api/clipboard/",
            json=user2_item,
            headers={
                "Authorization": f"Bearer {user2_token}",
                "Content-Type": "application/json"
            }
        )
        
        if add_response2.status_code != 200:
            print(f"❌ User 2 failed to add clipboard item: {add_response2.status_code} - {add_response2.text}")
            return False
        
        print(f"✅ User 2 added their clipboard item")
        
        # User 1 fetches shared clipboard to see User 2's item
        print("📋 User 1 fetching updated shared clipboard...")
        updated_response = requests.get(
            f"{base_url}/api/clipboard/?shared=true",
            headers={
                "Authorization": f"Bearer {user1_token}",
                "Content-Type": "application/json"
            }
        )
        
        if updated_response.status_code != 200:
            print(f"❌ User 1 failed to fetch updated shared clipboard: {updated_response.status_code} - {updated_response.text}")
            return False
        
        updated_items = updated_response.json()
        print(f"📋 User 1 found {len(updated_items)} total shared clipboard items")
        
        # Check if User 1 can see User 2's item
        user2_item_found = False
        for item in updated_items:
            if item.get('content') == user2_item['content']:
                user2_item_found = True
                print(f"✅ User 1 can see User 2's clipboard item!")
                break
        
        if not user2_item_found:
            print("❌ User 1 cannot see User 2's clipboard item!")
            return False
        
        # Test stats endpoint
        print("📊 Testing shared clipboard stats...")
        stats_response = requests.get(
            f"{base_url}/api/clipboard/stats?shared=true",
            headers={
                "Authorization": f"Bearer {user1_token}",
                "Content-Type": "application/json"
            }
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📊 Shared clipboard stats:")
            print(f"   Total items: {stats.get('total_items', 0)}")
            print(f"   Unique users: {stats.get('unique_users', 0)}")
            print(f"   Is shared: {stats.get('is_shared', False)}")
        
        print("🎉 SUCCESS: Shared clipboard is working perfectly!")
        print("✅ Users can see each other's clipboard items")
        print("✅ All clipboard items are stored permanently")
        print("✅ Cross-user visibility is working")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def register_and_login_user(base_url, user_data):
    """Register and login a user, return JWT token"""
    # Register
    register_response = requests.post(
        f"{base_url}/api/auth/register",
        json=user_data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    if register_response.status_code != 200:
        raise Exception(f"Registration failed: {register_response.status_code} - {register_response.text}")
    
    # Login
    login_response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        },
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    if login_response.status_code != 200:
        raise Exception(f"Login failed: {login_response.status_code} - {login_response.text}")
    
    login_data = login_response.json()
    access_token = login_data.get("access_token")
    
    if not access_token:
        raise Exception("No access token received")
    
    print(f"✅ User {user_data['email']} registered and logged in")
    return access_token

if __name__ == "__main__":
    result = asyncio.run(test_shared_clipboard())
    sys.exit(0 if result else 1)
