#!/usr/bin/env python3
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv("backend/.env")

async def check_firebase_audit_logs():
    """Directly check Firebase audit logs collection"""
    
    try:
        # Initialize Firebase
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        if not credentials_path or not os.path.exists(credentials_path):
            print(f"❌ Firebase credentials not found: {credentials_path}")
            return
            
        # Check if Firebase is already initialized
        try:
            firebase_admin.get_app()
            print("✅ Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred, {'projectId': project_id})
            print(f"✅ Firebase initialized for project: {project_id}")
        
        # Get Firestore client
        db = firestore.client()
        
        # Check all audit logs
        print(f"\n🔍 Checking all audit logs in collection...")
        audit_logs_ref = db.collection('audit_logs')
        docs = audit_logs_ref.limit(10).get()  # Get first 10 logs
        
        print(f"Found {len(docs)} audit logs in total:")
        
        for i, doc in enumerate(docs):
            data = doc.to_dict()
            print(f"\n📝 Log {i+1} (ID: {doc.id}):")
            print(f"   Action: {data.get('action', 'N/A')}")
            print(f"   User ID: {data.get('user_id', 'N/A')}")
            print(f"   Details: {data.get('details', 'N/A')}")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Created: {data.get('created_at', 'N/A')}")
        
        # Check for our specific user
        target_user_id = "LZ2ijVatwthne2YnzlSs8JUMk433"
        print(f"\n🎯 Checking logs for specific user: {target_user_id}")
        
        user_logs = audit_logs_ref.where('user_id', '==', target_user_id).get()
        print(f"Found {len(user_logs)} logs for user {target_user_id}:")
        
        for i, doc in enumerate(user_logs):
            data = doc.to_dict()
            print(f"\n   Log {i+1}: {data.get('action')} - {data.get('details')}")
            
        if len(user_logs) == 0:
            print(f"❌ No logs found for user {target_user_id}")
            
            # Let's check what user_ids actually exist
            print(f"\n🔍 Checking what user_ids exist in audit logs...")
            all_logs = audit_logs_ref.get()
            user_ids = set()
            for doc in all_logs:
                data = doc.to_dict()
                user_id = data.get('user_id')
                if user_id:
                    user_ids.add(user_id)
            
            print(f"Found user_ids: {list(user_ids)}")
        
    except Exception as e:
        print(f"❌ Error checking Firebase: {e}")

if __name__ == "__main__":
    asyncio.run(check_firebase_audit_logs())
