import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.firebase_service import FirebaseService

async def list_all_users():
    """List all users in Firebase to see what's stored"""
    try:
        await FirebaseService.initialize()
        print("✅ Firebase initialized")
        
        # Get all users from the users collection
        print("📋 Listing all users in Firebase...")
        
        # Access the database directly to see all users
        if FirebaseService._db:
            users_ref = FirebaseService._db.collection('users')
            docs = users_ref.stream()
            
            count = 0
            for doc in docs:
                count += 1
                user_data = doc.to_dict()
                print(f"User {count}: ID={doc.id}, Data={user_data}")
            
            if count == 0:
                print("❌ No users found in Firebase")
            else:
                print(f"✅ Found {count} users in Firebase")
        else:
            print("❌ Firebase database not available")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(list_all_users())
