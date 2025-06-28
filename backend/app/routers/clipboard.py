"""
Clipboard Router for ClipVault (Firebase)

Handles clipboard item management using Firebase Firestore.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.firebase_service import FirebaseService
from firebase_admin import firestore
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Clipboard router is working"}

@router.get("/test-shared")
async def test_shared_endpoint():
    """Test endpoint for shared clipboard functionality"""
    try:
        print("🧪 Testing shared clipboard functionality")
        
        # Test if the service method exists
        if hasattr(FirebaseService, 'get_all_clipboard_items'):
            print("✅ get_all_clipboard_items method exists")
            items = await FirebaseService.get_all_clipboard_items(limit=10)
            return {
                "status": "success",
                "message": "Shared clipboard is working",
                "items_count": len(items),
                "items": items[:3]  # Return first 3 items
            }
        else:
            return {
                "status": "error", 
                "message": "get_all_clipboard_items method not found"
            }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

# Pydantic models for clipboard operations
class ClipboardItemCreate(BaseModel):
    content: str
    content_type: str = "text"
    domain: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ClipboardItemResponse(BaseModel):
    id: str
    content: str
    content_type: str = "text"
    domain: Optional[str] = None
    user_id: Optional[str] = None
    created_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Helper function to get user ID from request
async def get_current_user_id(request: Request) -> str:
    """Extract user ID from JWT token in Authorization header"""
    import jwt
    import os
    
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        print("⚠️ No auth header provided, cannot extract user ID")
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token and decode properly
    token = auth_header.replace("Bearer ", "")
    
    try:
        # Use the same JWT settings as auth.py
        SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
        ALGORITHM = os.getenv("ALGORITHM", "HS256")
        
        # Decode and verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            print("⚠️ No user ID found in JWT token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        print(f"✅ Extracted user ID from JWT: {user_id}")
        return user_id
        
    except jwt.ExpiredSignatureError:
        print("⚠️ JWT token has expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        print(f"⚠️ Invalid JWT token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"⚠️ Error decoding JWT token: {e}")
        raise HTTPException(status_code=401, detail="Token decode error")

@router.get("/")
async def get_clipboard_items(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    shared: bool = Query(False, description="Include shared clipboard items from all users")
):
    """Get clipboard items - can include shared items from all users when shared=true"""
    try:
        user_id = await get_current_user_id(request)
        print(f"📋 Getting clipboard items for user: {user_id} (shared={shared})")
        
        if shared:
            # SHARED MODE: Get ALL clipboard items from ALL users
            print("🌐 SHARED MODE: Getting clipboard items from all users")
            try:
                print("🧪 About to call FirebaseService.get_all_clipboard_items...")
                items = await FirebaseService.get_all_clipboard_items(limit, offset)
                print(f"📋 Shared mode: Found {len(items)} items from all users")
            except Exception as e:
                print(f"❌ Shared mode failed: {e}")
                import traceback
                traceback.print_exc()
                print("🔄 Falling back to user items")
                items = await FirebaseService.get_user_clipboard_items(user_id, limit, offset)
        else:
            # PRIVATE MODE: Get only user's own clipboard items
            items = await FirebaseService.get_user_clipboard_items(user_id, limit, offset)
            print(f"📋 Found {len(items)} private clipboard items for user {user_id}")
        
        return items
        
    except Exception as e:
        print(f"❌ Error fetching clipboard items: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to fetch clipboard items: {str(e)}")

@router.post("/", response_model=ClipboardItemResponse)
async def create_clipboard_item(
    item_data: ClipboardItemCreate,
    request: Request
):
    """Create a new clipboard item"""
    try:
        user_id = await get_current_user_id(request)
        print(f"📋 Creating clipboard item for user: {user_id}")
        print(f"📋 Item content: {item_data.content[:50]}...")
        
        # Prepare clipboard item data for Firebase
        new_item_data = {
            "content": item_data.content,
            "content_type": item_data.content_type,
            "domain": item_data.domain,
            "user_id": user_id,
            "metadata": item_data.metadata or {}
        }
        
        # Create clipboard item in Firebase
        item_id = await FirebaseService.create_clipboard_item(new_item_data)
        print(f"📋 Created clipboard item with ID: {item_id}")
        
        # Return the created item with ID
        new_item_data["id"] = item_id
        new_item_data["created_at"] = datetime.utcnow().isoformat()
        
        print(f"✅ Created clipboard item: {item_data.content[:50]}... ({item_id})")
        
        return new_item_data
        
    except Exception as e:
        print(f"Error creating clipboard item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create clipboard item")

@router.delete("/{item_id}")
async def delete_clipboard_item(
    item_id: str,
    request: Request
):
    """Delete a clipboard item - DISABLED for shared clipboard"""
    raise HTTPException(
        status_code=403, 
        detail="Deleting clipboard items is not allowed in shared mode. All items are permanently stored."
    )

@router.delete("/clear")
async def clear_all_clipboard_items(request: Request):
    """Clear all clipboard items - DISABLED for shared clipboard"""
    raise HTTPException(
        status_code=403,
        detail="Clearing clipboard items is not allowed in shared mode. All items are permanently stored."
    )

@router.get("/search/{query}")
async def search_clipboard_items(
    query: str,
    request: Request,
    limit: int = Query(20, ge=1, le=50),
    shared: bool = Query(True, description="Search shared clipboard items from all users")
):
    """Search clipboard items by content - defaults to shared mode"""
    try:
        user_id = await get_current_user_id(request)
        print(f"🔍 Searching clipboard items for query: '{query}' (shared={shared})")
        
        if shared:
            # Search all clipboard items from all users
            all_items = await FirebaseService.get_all_clipboard_items(limit=1000, offset=0)
            print(f"🔍 Searching through {len(all_items)} shared items")
        else:
            # Search only user's own items
            all_items = await FirebaseService.get_user_clipboard_items(user_id, limit=1000, offset=0)
            print(f"🔍 Searching through {len(all_items)} personal items")
        
        # Filter items that match the search query
        matching_items = []
        for item in all_items:
            content = item.get('content', '').lower()
            if query.lower() in content:
                matching_items.append(item)
        
        print(f"🔍 Found {len(matching_items)} matching items")
        return matching_items[:limit]
        
    except Exception as e:
        print(f"Error searching clipboard items: {e}")
        raise HTTPException(status_code=500, detail="Failed to search clipboard items")

@router.get("/stats")
async def get_clipboard_stats(
    request: Request,
    shared: bool = Query(True, description="Get shared clipboard stats from all users")
):
    """Get clipboard statistics - defaults to shared mode"""
    try:
        user_id = await get_current_user_id(request)
        print(f"📊 Getting clipboard stats (shared={shared})")
        
        if shared:
            # Get ALL clipboard items from ALL users for shared stats
            all_items = await FirebaseService.get_all_clipboard_items(limit=10000, offset=0)
            print(f"📊 Calculating stats from {len(all_items)} shared items")
        else:
            # Get only user's own items
            all_items = await FirebaseService.get_user_clipboard_items(user_id, limit=1000, offset=0)
            print(f"📊 Calculating stats from {len(all_items)} personal items")
        
        # Calculate real statistics
        total_items = len(all_items)
        
        # Count by content type
        text_items = sum(1 for item in all_items if item.get('content_type') == 'text')
        image_items = sum(1 for item in all_items if item.get('content_type') == 'image')
        file_items = sum(1 for item in all_items if item.get('content_type') == 'file')
        
        # Calculate items in last 24 hours
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        recent_items = 0
        
        for item in all_items:
            try:
                item_time = datetime.fromisoformat(item.get('created_at', '').replace('Z', ''))
                if item_time > last_24h:
                    recent_items += 1
            except (ValueError, TypeError):
                continue
        
        # Calculate total data size (estimate)
        total_size_bytes = sum(len(item.get('content', '').encode('utf-8')) for item in all_items)
        total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
        
        # Count unique users (only in shared mode)
        unique_users = len(set(item.get('user_id', '') for item in all_items if item.get('user_id'))) if shared else 1
        
        stats = {
            "total_items": total_items,
            "text_items": text_items,
            "image_items": image_items,
            "file_items": file_items,
            "recent_items": recent_items,
            "total_size_mb": total_size_mb,
            "sync_count": total_items,  # Assuming each item represents a sync
            "unique_users": unique_users,
            "is_shared": shared
        }
        
        print(f"📊 Clipboard stats: {stats}")
        return stats
        
    except Exception as e:
        print(f"Error fetching clipboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch clipboard stats")