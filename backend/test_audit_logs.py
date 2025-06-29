#!/usr/bin/env python3
"""
Test script to check audit logs in Firebase
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.firebase_service import FirebaseService

async def test_audit_logs():
    print('🔍 Testing audit logs...')
    try:
        await FirebaseService.initialize()
        
        # Try to get audit logs for demo users
        demo_user_ids = ['demo-user-123', 'demo-user-456']
        
        for user_id in demo_user_ids:
            print(f'📜 Checking audit logs for user: {user_id}')
            logs = await FirebaseService.get_user_audit_logs(user_id, limit=10)
            print(f'Found {len(logs)} audit logs for {user_id}')
            
            for log in logs[:3]:  # Show first 3 logs
                print(f'  - {log.get("action", "N/A")}: {log.get("details", "N/A")}')
        
        # Also check all audit logs without user filter
        print('📋 Checking all audit logs in collection...')
        try:
            query = FirebaseService._db.collection('audit_logs').limit(10)
            docs = await FirebaseService._run_in_executor(query.get)
            print(f'Found {len(docs)} total audit log documents')
            
            for doc in docs:
                data = doc.to_dict()
                print(f'  - {data.get("action", "N/A")}: User {data.get("user", "N/A")} at {data.get("timestamp", "N/A")}')
        except Exception as e:
            print(f'Error fetching all audit logs: {e}')
    except Exception as e:
        print(f'Error in test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_audit_logs())
