"""
Firebase Database Setup and Initialization Script

This script creates the Firebase Firestore database structure, sets up collections,
and initializes the database with default data and security rules.

Run this script once to set up your Firebase database for ClipVault.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.firebase_service import FirebaseService
from app.models.models import (
    User, Device, ClipboardItem, SecurityEvent, AuditLog, 
    SecurityPolicy, Session, UserRole, DeviceType, ContentType,
    SecurityEventSeverity, SecurityEventType, AuditStatus
)

class FirebaseDatabaseCreator:
    """Creates and initializes Firebase Firestore database for ClipVault"""
    
    def __init__(self):
        self.firebase_service = None
        self.collections = {
            'users': 'users',
            'devices': 'devices',
            'clipboard_items': 'clipboard_items',
            'security_events': 'security_events',
            'audit_logs': 'audit_logs',
            'security_policies': 'security_policies',
            'sessions': 'sessions'
        }

    async def initialize_firebase(self):
        """Initialize Firebase service"""
        print("🔥 Initializing Firebase service...")
        await FirebaseService.initialize()
        self.firebase_service = FirebaseService()
        print("✅ Firebase service initialized successfully")

    async def create_collections(self):
        """Create all Firestore collections with sample documents"""
        print("\n📦 Creating Firestore collections...")
        
        # Create collections by adding sample documents (which can be deleted later)
        for collection_name in self.collections.values():
            try:
                # Add a temporary document to create the collection
                temp_doc = {
                    'id': 'temp_init_doc',
                    'created_at': datetime.utcnow().isoformat(),
                    'temp': True,
                    'description': f'Temporary document to initialize {collection_name} collection'
                }
                
                doc_ref = self.firebase_service.db.collection(collection_name).document('temp_init_doc')
                await doc_ref.set(temp_doc)
                print(f"✅ Created collection: {collection_name}")
                
                # Delete the temporary document
                await doc_ref.delete()
                print(f"🗑️  Cleaned up temporary document in {collection_name}")
                
            except Exception as e:
                print(f"❌ Error creating collection {collection_name}: {str(e)}")

    async def create_admin_user(self):
        """Create default admin user"""
        print("\n👤 Creating default admin user...")
        
        admin_user_data = {
            'id': 'admin-001',
            'email': 'admin@clipvault.com',
            'name': 'ClipVault Administrator',
            'hashed_password': '$2b$12$example_hashed_password',  # Replace with actual hashed password
            'role': UserRole.ADMIN.value,
            'organization': 'ClipVault',
            'is_active': True,
            'firebase_uid': None,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': None
        }
        
        try:
            result = await self.firebase_service.create_document('users', admin_user_data)
            if result:
                print("✅ Admin user created successfully")
                return admin_user_data['id']
            else:
                print("❌ Failed to create admin user")
                return None
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            return None

    async def create_default_security_policy(self, user_id: str):
        """Create default security policy for admin user"""
        print("\n🔒 Creating default security policy...")
        
        security_policy_data = {
            'id': 'default-policy-001',
            'user_id': user_id,
            'policy_name': 'Default Security Policy',
            'encryption_algorithm': 'AES-256',
            'key_rotation_interval': 30,
            'session_timeout': 30,
            'max_failed_attempts': 5,
            'require_two_factor': False,
            'enable_biometric': False,
            'allow_guest_access': False,
            'rate_limit': 60,
            'domain_whitelist': ['localhost', '127.0.0.1'],
            'ip_whitelist': [],
            'threat_detection_enabled': True,
            'auto_block_threats': True,
            'block_duration': 300,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': None
        }
        
        try:
            result = await self.firebase_service.create_document('security_policies', security_policy_data)
            if result:
                print("✅ Default security policy created successfully")
            else:
                print("❌ Failed to create default security policy")
        except Exception as e:
            print(f"❌ Error creating security policy: {str(e)}")

    async def create_sample_data(self, user_id: str):
        """Create sample data for testing"""
        print("\n📋 Creating sample data...")
        
        # Sample device
        device_data = {
            'id': 'device-001',
            'user_id': user_id,
            'name': 'Development Machine',
            'device_type': DeviceType.DESKTOP.value,
            'platform': 'Windows 11',
            'fingerprint': 'dev-machine-fingerprint-001',
            'ip_address': '127.0.0.1',
            'user_agent': 'ClipVault/1.0.0 (Windows NT 10.0; Win64; x64)',
            'is_trusted': True,
            'is_online': True,
            'last_seen': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Sample clipboard item
        clipboard_data = {
            'id': 'clip-001',
            'user_id': user_id,
            'device_id': 'device-001',
            'content': 'Welcome to ClipVault! This is a sample clipboard item.',
            'encrypted_content': None,
            'content_type': ContentType.TEXT.value,
            'content_hash': 'sample_hash_001',
            'iv': None,
            'is_encrypted': False,
            'domain': 'localhost',
            'metadata': {
                'source': 'manual',
                'category': 'sample',
                'tags': ['welcome', 'sample']
            },
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Sample security event
        security_event_data = {
            'id': 'security-001',
            'user_id': user_id,
            'event_type': SecurityEventType.AUTHENTICATION.value,
            'severity': SecurityEventSeverity.LOW.value,
            'description': 'User logged in successfully',
            'source_ip': '127.0.0.1',
            'user_agent': 'ClipVault/1.0.0',
            'is_blocked': False,
            'details': {
                'login_method': 'email',
                'success': True
            },
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Sample audit log
        audit_log_data = {
            'id': 'audit-001',
            'user_id': user_id,
            'action': 'database_initialized',
            'resource_type': 'system',
            'resource_id': 'firebase_setup',
            'details': {
                'collections_created': len(self.collections),
                'setup_version': '1.0.0'
            },
            'ip_address': '127.0.0.1',
            'user_agent': 'ClipVault Setup Script',
            'status': AuditStatus.SUCCESS.value,
            'hash_chain': None,
            'created_at': datetime.utcnow().isoformat()
        }
        
        try:
            # Create sample documents
            await self.firebase_service.create_document('devices', device_data)
            print("✅ Sample device created")
            
            await self.firebase_service.create_document('clipboard_items', clipboard_data)
            print("✅ Sample clipboard item created")
            
            await self.firebase_service.create_document('security_events', security_event_data)
            print("✅ Sample security event created")
            
            await self.firebase_service.create_document('audit_logs', audit_log_data)
            print("✅ Sample audit log created")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {str(e)}")

    async def create_indexes(self):
        """Create Firestore indexes for better query performance"""
        print("\n📊 Creating Firestore indexes...")
        print("ℹ️  Firestore indexes need to be created manually in the Firebase Console.")
        print("   Recommended indexes:")
        print("   - Collection: users, Fields: email (Ascending)")
        print("   - Collection: devices, Fields: user_id (Ascending), is_online (Ascending)")
        print("   - Collection: clipboard_items, Fields: user_id (Ascending), created_at (Descending)")
        print("   - Collection: security_events, Fields: user_id (Ascending), severity (Ascending)")
        print("   - Collection: audit_logs, Fields: user_id (Ascending), created_at (Descending)")

    def create_firestore_rules(self):
        """Generate Firestore security rules"""
        print("\n🔐 Generating Firestore security rules...")
        
        rules = """
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only access their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Devices belong to users
    match /devices/{deviceId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Clipboard items belong to users
    match /clipboard_items/{itemId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Security events belong to users (read-only for users)
    match /security_events/{eventId} {
      allow read: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
      allow write: if request.auth != null && 
        request.auth.token.role == 'admin';
    }
    
    // Audit logs belong to users (read-only for users)
    match /audit_logs/{logId} {
      allow read: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
      allow write: if request.auth != null && 
        request.auth.token.role == 'admin';
    }
    
    // Security policies belong to users
    match /security_policies/{policyId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
    
    // Sessions belong to users
    match /sessions/{sessionId} {
      allow read, write: if request.auth != null && 
        request.auth.uid == resource.data.user_id;
    }
  }
}
"""
        
        # Save rules to file
        rules_file = os.path.join(os.path.dirname(__file__), 'firestore.rules')
        with open(rules_file, 'w') as f:
            f.write(rules)
        
        print(f"✅ Firestore rules saved to: {rules_file}")
        print("   Apply these rules in the Firebase Console -> Firestore Database -> Rules")

    async def verify_setup(self):
        """Verify that the database setup was successful"""
        print("\n🔍 Verifying database setup...")
        
        try:
            # Check if collections exist by trying to list them
            for collection_name in self.collections.values():
                docs = await self.firebase_service.list_documents(collection_name, limit=1)
                print(f"✅ Collection '{collection_name}' is accessible")
            
            # Check if admin user exists
            admin_user = await self.firebase_service.get_document('users', 'admin-001')
            if admin_user:
                print("✅ Admin user exists and is accessible")
            else:
                print("❌ Admin user not found")
            
            print("\n🎉 Database setup verification completed!")
            
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")

    async def run_setup(self):
        """Run the complete database setup process"""
        print("🚀 Starting Firebase Database Setup for ClipVault")
        print("=" * 60)
        
        try:
            # Initialize Firebase
            await self.initialize_firebase()
            
            # Create collections
            await self.create_collections()
            
            # Create admin user
            admin_user_id = await self.create_admin_user()
            
            if admin_user_id:
                # Create default security policy
                await self.create_default_security_policy(admin_user_id)
                
                # Create sample data
                await self.create_sample_data(admin_user_id)
            
            # Create indexes (instructions)
            await self.create_indexes()
            
            # Generate security rules
            self.create_firestore_rules()
            
            # Verify setup
            await self.verify_setup()
            
            print("\n" + "=" * 60)
            print("🎉 Firebase Database Setup Complete!")
            print("\n📋 Next Steps:")
            print("1. Apply the Firestore security rules in Firebase Console")
            print("2. Create the recommended indexes in Firebase Console")
            print("3. Update the admin user password hash")
            print("4. Test the API endpoints at http://localhost:8001/docs")
            print("5. Start building your frontend!")
            
        except Exception as e:
            print(f"\n❌ Setup failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Close Firebase connection
            if self.firebase_service:
                await FirebaseService.close()

if __name__ == "__main__":
    # Check if environment variables are set
    required_env_vars = [
        'FIREBASE_PROJECT_ID',
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file and try again.")
        sys.exit(1)
    
    # Run the setup
    creator = FirebaseDatabaseCreator()
    asyncio.run(creator.run_setup())
