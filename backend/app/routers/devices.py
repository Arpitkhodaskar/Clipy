"""
Devices Router for ClipVault - device management using Firebase Firestore.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.firebase_service import FirebaseService
from datetime import datetime
import uuid
import jwt
import os

router = APIRouter()

# Pydantic models for device operations
class DeviceCreate(BaseModel):
    name: str
    device_type: str = "desktop"  # desktop, mobile, tablet
    platform: Optional[str] = None
    browser: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DeviceResponse(BaseModel):
    id: str
    name: str
    device_type: str
    platform: Optional[str] = None
    browser: Optional[str] = None
    user_id: str
    is_trusted: bool = False
    is_online: bool = False
    last_seen: str
    created_at: str
    metadata: Optional[Dict[str, Any]] = None

# Helper function to get user ID from request
async def get_current_user_id(request: Request) -> str:
    """Extract user ID from JWT token in Authorization header"""
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

@router.get("/", response_model=List[DeviceResponse])
async def get_devices(request: Request):
    """Get devices for the authenticated user"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get real devices from Firebase
        devices = await FirebaseService.get_user_devices(user_id)
        
        return devices
        
    except Exception as e:
        print(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch devices")

@router.post("/", response_model=DeviceResponse)
async def register_device(
    device_data: DeviceCreate,
    request: Request
):
    """Register a new device"""
    try:
        user_id = await get_current_user_id(request)
        
        # Prepare device data for Firebase
        new_device_data = {
            "name": device_data.name,
            "device_type": device_data.device_type,
            "platform": device_data.platform or "Unknown",
            "browser": device_data.browser or "Unknown",
            "user_id": user_id,
            "is_trusted": False,
            "is_online": True,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "ip_address": request.client.host if request.client else "unknown",
            "metadata": device_data.metadata or {}
        }
        
        # Create device in Firebase
        device_id = await FirebaseService.create_device(new_device_data)
        
        # Get the created device
        created_device = await FirebaseService.get_device_by_id(device_id)
        
        return created_device
        
    except Exception as e:
        print(f"Error registering device: {e}")
        raise HTTPException(status_code=500, detail="Failed to register device")
