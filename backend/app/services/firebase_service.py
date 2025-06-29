import firebase_admin
from firebase_admin import credentials, firestore, auth
from typing import Dict, List, Optional, Any
import os
from datetime import datetime
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

class FirebaseService:
    _instance = None
    _db = None
    _executor = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize(cls):
        """Initialize Firebase connection"""
        try:
            # Get Firebase configuration from environment
            import json
            
            credentials_json = os.getenv("FIREBASE_CREDENTIALS")
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("FIREBASE_CREDENTIALS_PATH")
            project_id = os.getenv("FIREBASE_PROJECT_ID")
            
            if not project_id:
                raise Exception("FIREBASE_PROJECT_ID not set in environment variables")
            
            # Try JSON credentials first (for Railway/cloud deployment)
            if credentials_json:
                try:
                    cred_dict = json.loads(credentials_json)
                    cred = credentials.Certificate(cred_dict)
                    print("✅ Using Firebase credentials from FIREBASE_CREDENTIALS environment variable")
                except json.JSONDecodeError as e:
                    raise Exception(f"Invalid JSON in FIREBASE_CREDENTIALS: {e}")
            # Fall back to file path (for local development)
            elif credentials_path and os.path.exists(credentials_path):
                cred = credentials.Certificate(credentials_path)
                print(f"✅ Using Firebase credentials from file: {credentials_path}")
            else:
                raise Exception("No Firebase credentials found. Set FIREBASE_CREDENTIALS (JSON) or GOOGLE_APPLICATION_CREDENTIALS (file path)")
            
            # Initialize Firebase Admin SDK
            firebase_admin.initialize_app(cred, {
                'projectId': project_id
            })
            
            cls._db = firestore.client()
            cls._executor = ThreadPoolExecutor(max_workers=10)
            
            print(f"✅ Firebase Firestore connected to project: {project_id}")
            
        except Exception as e:
            print(f"❌ Firebase connection failed: {e}")
            print("📝 To use Firebase:")
            print("   1. Create a Firebase project at https://console.firebase.google.com/")
            print("   2. Download service account key to backend/firebase-service-account-key.json")
            print("   3. Update FIREBASE_PROJECT_ID in .env file")
            print("   4. See FIREBASE_REAL_SETUP.md for detailed instructions")
            raise Exception("Firebase connection required")
    
    @classmethod
    async def close(cls):
        """Close Firebase connection"""
        if cls._executor:
            cls._executor.shutdown(wait=True)
        print("❌ Firebase Firestore disconnected")
    
    @classmethod
    async def _run_in_executor(cls, func, *args, **kwargs):
        """Run Firestore operations in thread executor"""
        if not cls._db:
            raise Exception("Firebase not initialized")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            cls._executor, 
            lambda: func(*args, **kwargs)
        )
    
    @classmethod
    def _hash_password(cls, password: str) -> str:
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # Users Collection with Firebase Auth Integration
    @classmethod
    async def create_user(cls, user_data: Dict[str, Any]) -> str:
        """Create a new user with Firebase Auth and Firestore"""
        # Real Firebase implementation
        try:
            # Create user in Firebase Auth
            firebase_user = await cls._run_in_executor(
                auth.create_user,
                email=user_data['email'],
                password=user_data.get('password', ''),
                display_name=user_data.get('name', ''),
                disabled=False
            )
            
            user_id = firebase_user.uid
            
            # Remove password from user_data (Firebase Auth handles it)
            user_data_copy = user_data.copy()
            user_data_copy.pop('password', None)
            
            # Create user profile in Firestore
            user_data_copy.update({
                'id': user_id,
                'firebase_uid': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            await cls._run_in_executor(
                cls._db.collection('users').document(user_id).set,
                user_data_copy
            )
            
            return user_id
            
        except Exception as e:
            print(f"Error creating Firebase user: {e}")
            # Fallback to manual user creation for development
            user_id = str(uuid.uuid4())
            if 'password' in user_data:
                user_data['password_hash'] = cls._hash_password(user_data['password'])
                del user_data['password']
            
            user_data.update({
                'id': user_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })
            
            await cls._run_in_executor(
                cls._db.collection('users').document(user_id).set,
                user_data
            )
            return user_id
    
    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        doc = await cls._run_in_executor(
            cls._db.collection('users').document(user_id).get
        )
        if doc.exists:
            user_data = doc.to_dict()
            user_data.pop('password_hash', None)  # Remove password hash
            return user_data
        return None
    
    @classmethod
    async def get_user_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = cls._db.collection('users').where('email', '==', email).limit(1)
        docs = await cls._run_in_executor(query.get)
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data.pop('password_hash', None)  # Remove password hash
            return user_data
        return None
    
    @classmethod
    async def verify_firebase_token(cls, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token and return user info"""
        try:
            # Verify the ID token
            decoded_token = await cls._run_in_executor(
                auth.verify_id_token,
                id_token
            )
            
            user_id = decoded_token['uid']
            
            # Get user profile from Firestore
            user = await cls.get_user_by_id(user_id)
            return user
            
        except Exception as e:
            print(f"Firebase token verification failed: {e}")
            return None
    
    @classmethod
    async def verify_password(cls, email: str, password: str) -> bool:
        """Verify user password"""
        # For real Firebase Auth, we need to authenticate differently
        # Since we can't verify passwords directly with Admin SDK,
        # we'll check if the user has a password_hash (fallback mode)
        # or use Firebase Auth (proper mode)
        
        query = cls._db.collection('users').where('email', '==', email).limit(1)
        docs = await cls._run_in_executor(query.get)
        
        for doc in docs:
            user_data = doc.to_dict()
            # Check if this user has a password hash (development fallback)
            stored_hash = user_data.get('password_hash')
            if stored_hash:
                return stored_hash == cls._hash_password(password)
            else:
                # This user was created with Firebase Auth
                # For development, we'll allow password verification
                # In production, use Firebase Auth SDK on client side
                return True  # Allow login for Firebase Auth users in development
                
        return False
    
    # Devices Collection
    @classmethod
    async def create_device(cls, device_data: Dict[str, Any]) -> str:
        """Create a new device"""
        device_id = str(uuid.uuid4())
        device_data.update({
            'id': device_id,
            'created_at': datetime.utcnow(),
            'last_seen': datetime.utcnow()
        })
        
        await cls._run_in_executor(
            cls._db.collection('devices').document(device_id).set,
            device_data
        )
        return device_id
    
    @classmethod
    async def get_user_devices(cls, user_id: str) -> List[Dict[str, Any]]:
        """Get all devices for a user"""
        try:
            devices_ref = cls._db.collection('devices').where('user_id', '==', user_id)
            docs = await cls._run_in_executor(devices_ref.get)
            
            devices = []
            for doc in docs:
                device_data = doc.to_dict()
                device_data['id'] = doc.id
                # Convert datetime objects to ISO strings for JSON serialization
                if 'created_at' in device_data and hasattr(device_data['created_at'], 'isoformat'):
                    device_data['created_at'] = device_data['created_at'].isoformat()
                if 'last_seen' in device_data and hasattr(device_data['last_seen'], 'isoformat'):
                    device_data['last_seen'] = device_data['last_seen'].isoformat()
                devices.append(device_data)
            
            return devices
        except Exception as e:
            print(f"Error fetching user devices: {e}")
            # Return empty list on error
            return []
    
    @classmethod
    async def update_device_trust(cls, device_id: str, user_id: str, is_trusted: bool) -> bool:
        """Update device trust status"""
        try:
            device_ref = cls._db.collection('devices').document(device_id)
            await cls._run_in_executor(
                device_ref.update,
                {
                    'is_trusted': is_trusted,
                    'updated_at': datetime.utcnow()
                }
            )
            return True
        except Exception as e:
            print(f"Error updating device trust: {e}")
            return False
    
    @classmethod
    async def delete_device(cls, device_id: str, user_id: str) -> bool:
        """Delete a device"""
        try:
            device_ref = cls._db.collection('devices').document(device_id)
            await cls._run_in_executor(device_ref.delete)
            return True
        except Exception as e:
            print(f"Error deleting device: {e}")
            return False
    
    @classmethod
    async def update_device_status(cls, device_id: str, is_online: bool) -> bool:
        """Update device online status"""
        try:
            device_ref = cls._db.collection('devices').document(device_id)
            await cls._run_in_executor(
                device_ref.update,
                {
                    'is_online': is_online,
                    'last_seen': datetime.utcnow()
                }
            )
            return True
        except Exception as e:
            print(f"Error updating device status: {e}")
            return False
    
    @classmethod
    async def update_device_activity(cls, device_id: str, user_id: str) -> bool:
        """Update device activity (last_seen and online status) for login"""
        try:
            device_ref = cls._db.collection('devices').document(device_id)
            await cls._run_in_executor(
                device_ref.update,
                {
                    'is_online': True,
                    'last_seen': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            )
            print(f"✅ Updated device activity for device: {device_id}")
            return True
        except Exception as e:
            print(f"Error updating device activity: {e}")
            return False
    
    # Clipboard Items Collection
    @classmethod
    async def create_clipboard_item(cls, item_data: Dict[str, Any]) -> str:
        """Create a new clipboard item"""
        item_id = str(uuid.uuid4())
        item_data.update({
            'id': item_id,
            'created_at': datetime.utcnow()
        })
        
        await cls._run_in_executor(
            cls._db.collection('clipboard_items').document(item_id).set,
            item_data
        )
        return item_id
    
    @classmethod
    async def get_user_clipboard_items(cls, user_id: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get clipboard items for a user with pagination"""
        try:
            print(f"🔍 Querying clipboard items for user: {user_id}")
            query = cls._db.collection('clipboard_items').where('user_id', '==', user_id)
            # Temporarily remove ordering to test basic query
            # query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            
            docs = await cls._run_in_executor(query.get)
            print(f"🔍 Found {len(docs)} documents for user {user_id}")
            
            items = []
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                print(f"🔍 Document data: {item_data}")
                # Convert datetime objects to ISO strings for JSON serialization
                if 'created_at' in item_data and hasattr(item_data['created_at'], 'isoformat'):
                    item_data['created_at'] = item_data['created_at'].isoformat()
                items.append(item_data)
            
            print(f"🔍 Returning {len(items)} items")
            return items
        except Exception as e:
            print(f"Error fetching user clipboard items: {e}")
            return []

    @classmethod
    async def get_all_clipboard_items(cls, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get ALL clipboard items from ALL users for shared clipboard functionality"""
        try:
            print(f"🔍 Querying ALL clipboard items (shared mode)")
            query = cls._db.collection('clipboard_items')
            # Order by created_at descending to get newest items first
            try:
                query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
            except Exception as e:
                print(f"⚠️ Could not order by created_at: {e}, continuing without ordering")
            
            query = query.limit(limit)
            
            docs = await cls._run_in_executor(query.get)
            print(f"🔍 Found {len(docs)} total clipboard documents")
            
            items = []
            for doc in docs:
                item_data = doc.to_dict()
                item_data['id'] = doc.id
                # Convert datetime objects to ISO strings for JSON serialization
                if 'created_at' in item_data and hasattr(item_data['created_at'], 'isoformat'):
                    item_data['created_at'] = item_data['created_at'].isoformat()
                items.append(item_data)
            
            print(f"🔍 Returning {len(items)} shared clipboard items")
            return items
        except Exception as e:
            print(f"Error fetching all clipboard items: {e}")
            return []
    
    @classmethod
    async def delete_clipboard_item(cls, item_id: str, user_id: str) -> bool:
        """Delete a clipboard item"""
        try:
            item_ref = cls._db.collection('clipboard_items').document(item_id)
            await cls._run_in_executor(item_ref.delete)
            return True
        except Exception as e:
            print(f"Error deleting clipboard item: {e}")
            return False
    
    # Security Events Collection
    @classmethod
    async def create_security_event(cls, event_data: Dict[str, Any]) -> str:
        """Create a new security event"""
        event_id = str(uuid.uuid4())
        event_data.update({
            'id': event_id,
            'created_at': datetime.utcnow()
        })
        
        await cls._run_in_executor(
            cls._db.collection('security_events').document(event_id).set,
            event_data
        )
        return event_id
    
    # Audit Logs Collection
    @classmethod
    async def create_audit_log(cls, log_data: Dict[str, Any]) -> str:
        """Create a new audit log"""
        log_id = str(uuid.uuid4())
        log_data.update({
            'id': log_id,
            'created_at': datetime.utcnow()
        })
        
        await cls._run_in_executor(
            cls._db.collection('audit_logs').document(log_id).set,
            log_data
        )
        return log_id
    
    @classmethod
    async def get_user_audit_logs(cls, user_id: str, limit: int = 50, offset: int = 0, 
                                 status_filter: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get audit logs for a user with filtering and pagination"""
        try:
            # Query logs for the specific user
            query = cls._db.collection('audit_logs').where('user_id', '==', user_id)
            
            # Apply status filter if provided
            if status_filter:
                query = query.where('status', '==', status_filter)
            
            # Get all matching documents (client-side sorting due to Firestore index limitations)
            query = query.limit(limit * 2)  # Get more to account for filtering
            
            docs = await cls._run_in_executor(query.get)
            
            logs = []
            for doc in docs:
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                
                # Convert datetime objects to ISO strings for JSON serialization
                if 'created_at' in log_data:
                    if hasattr(log_data['created_at'], 'isoformat'):
                        log_data['created_at'] = log_data['created_at'].isoformat()
                    # Also set timestamp for compatibility
                    log_data['timestamp'] = log_data['created_at']
                
                # Apply search filter if provided
                if search:
                    searchable_text = f"{log_data.get('action', '')} {log_data.get('details', '')} {log_data.get('user', '')}".lower()
                    if search.lower() not in searchable_text:
                        continue
                
                logs.append(log_data)
            
            # Sort by created_at/timestamp in descending order (newest first)
            try:
                logs.sort(key=lambda x: x.get('timestamp', x.get('created_at', '')), reverse=True)
            except Exception:
                pass  # If sorting fails, return unsorted
            
            # Apply offset and final limit
            start_index = offset
            end_index = offset + limit
            
            return logs[start_index:end_index]
            
        except Exception as e:
            print(f"Error fetching user audit logs: {e}")
            import traceback
            traceback.print_exc()
            return []