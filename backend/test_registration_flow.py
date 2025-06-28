#!/usr/bin/env python3
"""
Test Registration Flow Directly
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app.services.firebase_service import FirebaseService
from app.routers.auth import extract_device_info

async def test_registration():
    print("🔥 Initializing Firebase...")
    await FirebaseService.initialize()
    
    # Test device info extraction
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    device_info = extract_device_info(user_agent)
    print(f"📱 Device info extracted: {device_info}")
    
    # Test user creation
    user_data = {
        "email": "test_device@example.com",
        "name": "Test Device User",
        "password": "password123",
        "organization": "Test Org",
        "role": "user",
        "is_active": True
    }
    
    try:
        # Check if user exists first
        existing_user = await FirebaseService.get_user_by_email(user_data["email"])
        if existing_user:
            print(f"👤 User already exists: {existing_user['id']}")
            user_id = existing_user['id']
        else:
            user_id = await FirebaseService.create_user(user_data)
            print(f"👤 User created: {user_id}")
        
        # Test device creation
        device_data = {
            "name": f"{device_info['device_name']} - {device_info['browser']}",
            "device_type": device_info['device_type'],
            "platform": device_info['platform'], 
            "browser": device_info['browser'],
            "user_id": user_id,
            "ip_address": "127.0.0.1",
            "is_trusted": True,
            "is_online": True,
            "user_agent": user_agent,
            "metadata": {
                "registration_device": True,
                "source": "test_registration"
            }
        }
        
        device_id = await FirebaseService.create_device(device_data)
        print(f"📱 Device created: {device_id}")
        
        # Test audit log creation
        audit_data = {
            "action": "Test User Registration",
            "user": user_data["email"],
            "device": device_data['name'],
            "status": "success",
            "ip_address": "127.0.0.1",
            "details": f"Test registration: {user_data['name']} with device {device_data['name']}",
            "user_id": user_id,
            "device_id": device_id,
            "metadata": {
                "email": user_data["email"],
                "organization": user_data.get("organization"),
                "platform": device_info['platform'],
                "browser": device_info['browser']
            }
        }
        
        audit_id = await FirebaseService.create_audit_log(audit_data)
        print(f"📋 Audit log created: {audit_id}")
        
        # Test retrieval
        devices = await FirebaseService.get_user_devices(user_id)
        print(f"📱 User devices: {len(devices)} found")
        for device in devices:
            print(f"  - {device['name']} ({device['device_type']})")
        
        audit_logs = await FirebaseService.get_user_audit_logs(user_id, limit=10)
        print(f"📋 User audit logs: {len(audit_logs)} found")
        for log in audit_logs[:3]:
            print(f"  - {log['action']} ({log['status']})")
        
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration())
