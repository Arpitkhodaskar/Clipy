import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.firebase_service import FirebaseService

async def test_firebase_user():
    """Test Firebase user operations"""
    try:
        await FirebaseService.initialize()
        print("✅ Firebase initialized")
        
        # Test getting user by email
        print("🔍 Looking up user: testuser@firebase.com")
        user = await FirebaseService.get_user_by_email('testuser@firebase.com')
        if user:
            print(f"✅ Found user: {user}")
            
            # Test password verification
            print("🔐 Testing password verification...")
            is_valid = await FirebaseService.verify_password('testuser@firebase.com', 'testpass123')
            print(f"Password valid: {is_valid}")
        else:
            print("❌ User not found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_firebase_user())
