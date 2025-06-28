#!/usr/bin/env python3
"""
Firebase Setup Validator for ClipVault
Validates Firebase configuration and creates initial collections.
"""

import os
import sys
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("📦 Run: pip install firebase-admin python-dotenv")
    sys.exit(1)

def load_environment():
    """Load environment variables"""
    env_path = backend_dir / '.env'
    if not env_path.exists():
        print("❌ .env file not found!")
        print(f"📁 Expected location: {env_path}")
        return False
    
    load_dotenv(env_path)
    print("✅ Environment variables loaded")
    return True

def validate_firebase_config():
    """Validate Firebase configuration"""
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CREDENTIALS_PATH")
    
    print("\n🔍 Validating Firebase Configuration...")
    
    if not project_id:
        print("❌ FIREBASE_PROJECT_ID not set in .env")
        return False
    print(f"✅ Project ID: {project_id}")
    
    if not credentials_path:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env")
        return False
    
    cred_file = backend_dir / credentials_path.replace('./', '')
    if not cred_file.exists():
        print(f"❌ Credentials file not found: {cred_file}")
        print("📝 Download from Firebase Console → Project Settings → Service Accounts")
        return False
    print(f"✅ Credentials file: {cred_file}")
    
    # Validate JSON format
    try:
        with open(cred_file, 'r') as f:
            cred_data = json.load(f)
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in cred_data:
                print(f"❌ Missing field in credentials: {field}")
                return False
        
        if cred_data.get('project_id') != project_id:
            print(f"❌ Project ID mismatch:")
            print(f"   .env: {project_id}")
            print(f"   credentials: {cred_data.get('project_id')}")
            return False
        
        print("✅ Credentials file format valid")
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        return False
    
    return True

def test_firebase_connection():
    """Test Firebase connection"""
    try:
        print("\n🔥 Testing Firebase Connection...")
        
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CREDENTIALS_PATH")
        
        # Initialize Firebase
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred, {'projectId': project_id})
        
        # Test Firestore connection
        db = firestore.client()
        
        # Try to write a test document
        test_doc = {
            'test': True,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'message': 'ClipVault Firebase connection test'
        }
        
        doc_ref = db.collection('_test').document('connection_test')
        doc_ref.set(test_doc)
        print("✅ Write test successful")
        
        # Try to read the document
        doc = doc_ref.get()
        if doc.exists:
            print("✅ Read test successful")
        else:
            print("❌ Read test failed")
            return False
        
        # Clean up test document
        doc_ref.delete()
        print("✅ Cleanup successful")
        
        print(f"🎉 Firebase connection successful to project: {project_id}")
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False

def create_initial_collections():
    """Create initial Firestore collections with sample data"""
    try:
        print("\n📚 Creating Initial Collections...")
        
        db = firestore.client()
        
        # Create collections structure
        collections = [
            'users',
            'devices', 
            'clipboard_items',
            'security_settings',
            'audit_logs'
        ]
        
        for collection_name in collections:
            # Create a sample document to initialize the collection
            sample_doc = {
                'created_at': firestore.SERVER_TIMESTAMP,
                'sample': True,
                'description': f'Sample document for {collection_name} collection'
            }
            
            db.collection(collection_name).document('_sample').set(sample_doc)
            print(f"✅ Created {collection_name} collection")
        
        print("🎉 All collections created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create collections: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 ClipVault Firebase Setup Validator")
    print("=" * 50)
    
    # Step 1: Load environment
    if not load_environment():
        sys.exit(1)
    
    # Step 2: Validate configuration
    if not validate_firebase_config():
        print("\n❌ Firebase configuration invalid!")
        print("📖 See FIREBASE_REAL_SETUP.md for setup instructions")
        sys.exit(1)
    
    # Step 3: Test connection
    if not test_firebase_connection():
        print("\n❌ Firebase connection failed!")
        print("🔧 Check your Firebase project settings and try again")
        sys.exit(1)
    
    # Step 4: Create collections
    if not create_initial_collections():
        print("\n⚠️  Collections creation failed, but connection works")
        print("🔧 Check Firestore security rules")
    
    print("\n🎉 Firebase Setup Complete!")
    print("✅ Your ClipVault backend is ready to use real Firebase!")
    print("🔄 Restart your backend server to use the new configuration")

if __name__ == "__main__":
    main()
