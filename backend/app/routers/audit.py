"""
Audit Logs Router for ClipVault (Firebase)

Handles audit log management using Firebase Firestore.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.firebase_service import FirebaseService
from datetime import datetime, timedelta
import uuid

router = APIRouter()

# Pydantic models for audit operations
class AuditLogResponse(BaseModel):
    id: str
    timestamp: str
    action: str
    user: str
    device: str
    status: str  # success, warning, error, info
    ip_address: str
    details: str
    hash_chain: Optional[str] = None
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
        
        print(f"✅ Extracted user ID from JWT for audit: {user_id}")
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

@router.get("/", response_model=List[AuditLogResponse])
async def get_audit_logs(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get audit logs for the authenticated user"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get real audit logs from Firebase
        logs = await FirebaseService.get_user_audit_logs(user_id, limit, offset, status_filter, search)
        
        return logs
        
    except Exception as e:
        print(f"Error fetching audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")

@router.get("/stats")
async def get_audit_stats(request: Request):
    """Get audit log statistics"""
    try:
        user_id = await get_current_user_id(request)
        
        # Get all audit logs to calculate real stats (increased limit to get more data)
        all_logs = await FirebaseService.get_user_audit_logs(user_id, limit=1000, offset=0)
        
        # Calculate real statistics
        total_events = len(all_logs)
        success_events = sum(1 for log in all_logs if log.get('status') == 'success')
        security_events = sum(1 for log in all_logs if log.get('status') in ['error', 'warning'])
        failed_attempts = sum(1 for log in all_logs if log.get('status') == 'error')
        
        # Calculate events in last 24 hours
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_24h_events = 0
        
        for log in all_logs:
            try:
                log_time = datetime.fromisoformat(log.get('timestamp', '').replace('Z', ''))
                if log_time > last_24h:
                    last_24h_events += 1
            except (ValueError, TypeError):
                continue
        
        # Calculate success rate
        success_rate = (success_events / total_events * 100) if total_events > 0 else 100.0
        
        stats = {
            "total_events": total_events,
            "success_rate": round(success_rate, 1),
            "security_events": security_events,
            "failed_attempts": failed_attempts,
            "last_24h": last_24h_events
        }
        
        return stats
        
    except Exception as e:
        print(f"Error fetching audit stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit stats")

@router.post("/")
async def create_audit_log(
    action: str,
    details: str,
    request: Request,
    status: str = "success",
    device: Optional[str] = None
):
    """Create a new audit log entry"""
    try:
        user_id = await get_current_user_id(request)
        
        # Create new audit log
        new_log = {
            "action": action,
            "user": "test@test.com",  # TODO: Get from JWT properly
            "device": device or "API",
            "status": status,
            "ip_address": request.client.host if request.client else "127.0.0.1",
            "details": details,
            "user_id": user_id,
            "metadata": {}
        }
        
        # Save to Firebase
        log_id = await FirebaseService.create_audit_log(new_log)
        
        return {"message": "Audit log created successfully", "id": log_id}
        
    except Exception as e:
        print(f"Error creating audit log: {e}")
        raise HTTPException(status_code=500, detail="Failed to create audit log")