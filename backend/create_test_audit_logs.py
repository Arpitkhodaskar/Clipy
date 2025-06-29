#!/usr/bin/env python3
"""
Create some test audit logs for demo users
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService

async def create_test_audit_logs():
    """Create some test audit logs for demo users"""
    try:
        print('🔥 Initializing Firebase...')
        await FirebaseService.initialize()
        
        demo_users = [
            {"id": "demo-user-123", "email": "test@test.com", "name": "Demo User"},
            {"id": "demo-user-456", "email": "demo@clipvault.com", "name": "ClipVault Demo"}
        ]
        
        for user in demo_users:
            print(f'📝 Creating test audit logs for {user["email"]}...')
            
            # Create a few different types of audit logs
            test_logs = [
                {
                    "action": "User Login",
                    "user": user["email"],
                    "device": "Windows 10 - Chrome 120",
                    "status": "success",
                    "ip_address": "192.168.1.100",
                    "details": f"User {user['name']} logged in successfully",
                    "user_id": user["id"],
                    "device_id": "test-device-1",
                    "metadata": {
                        "email": user["email"],
                        "platform": "Windows",
                        "browser": "Chrome",
                        "device_type": "desktop"
                    }
                },
                {
                    "action": "Clipboard Sync",
                    "user": user["email"],
                    "device": "Windows 10 - Chrome 120",
                    "status": "success",
                    "ip_address": "192.168.1.100",
                    "details": "Clipboard data synchronized successfully",
                    "user_id": user["id"],
                    "device_id": "test-device-1",
                    "metadata": {
                        "email": user["email"],
                        "sync_type": "automatic",
                        "data_size": "156 bytes"
                    }
                },
                {
                    "action": "Device Trust Update",
                    "user": user["email"],
                    "device": "Windows 10 - Chrome 120",
                    "status": "success",
                    "ip_address": "192.168.1.100",
                    "details": "Device marked as trusted",
                    "user_id": user["id"],
                    "device_id": "test-device-1",
                    "metadata": {
                        "email": user["email"],
                        "trust_status": "trusted",
                        "updated_by": "user"
                    }
                }
            ]
            
            for i, log_data in enumerate(test_logs):
                # Set timestamp to recent times (spread over last few hours)
                timestamp = datetime.utcnow() - timedelta(hours=i, minutes=i*10)
                log_data["timestamp"] = timestamp.isoformat()
                
                log_id = await FirebaseService.create_audit_log(log_data)
                print(f'  ✅ Created audit log: {log_data["action"]} ({log_id})')
        
        print('🎉 Test audit logs created successfully!')
        
        # Verify logs were created
        print('🔍 Verifying created logs...')
        for user in demo_users:
            logs = await FirebaseService.get_user_audit_logs(user["id"], limit=10)
            print(f'  📋 {user["email"]}: Found {len(logs)} audit logs')
            
    except Exception as e:
        print(f'❌ Error creating test audit logs: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(create_test_audit_logs())
