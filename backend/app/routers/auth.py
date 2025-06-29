"""
Authentication Router for ClipVault (Firebase)

Handles registration, login, logout, token refresh, and user info using Firebase Auth and Firestore.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.services.firebase_service import FirebaseService
from app.schemas.schemas import UserResponse
import os
import jwt
from datetime import datetime, timedelta

router = APIRouter()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class RegisterRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    organization: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

@router.post("/register", response_model=UserResponse)
async def register_user(data: RegisterRequest, request: Request):
    """
    Register endpoint using Firebase Firestore for user storage.
    Also creates device entry and audit log.
    """
    try:
        # Check if user already exists in Firebase
        existing_user = await FirebaseService.get_user_by_email(data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user in Firebase
        user_id = await FirebaseService.create_user({
            "email": data.email,
            "name": data.name,
            "password": data.password,
            "organization": data.organization,
            "role": "user",
            "is_active": True
        })
        
        # Get client IP and User-Agent for device detection
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Extract device information from User-Agent
        device_info = extract_device_info(user_agent)
        print(f"🔧 REGISTRATION DEBUG - Device info extracted: {device_info}")
        
        # Create device entry for this registration
        device_signature = f"{device_info['platform']}-{device_info['browser']}-{client_ip}"
        device_data = {
            "name": device_info['device_name'],
            "device_type": device_info['device_type'],
            "platform": device_info['platform'], 
            "browser": device_info['browser'],
            "user_id": user_id,
            "ip_address": client_ip,
            "is_trusted": True,  # First device is automatically trusted
            "is_online": True,
            "user_agent": user_agent,
            "metadata": {
                "device_signature": device_signature,
                "registration_device": True,
                "source": "user_registration",
                "os_version": device_info.get('os_version', 'Unknown'),
                "browser_version": device_info.get('browser_version', 'Unknown'),
                "registration_date": datetime.utcnow().isoformat()
            }
        }
        
        print(f"🔧 REGISTRATION DEBUG - Creating device with data: {device_data}")
        device_id = await FirebaseService.create_device(device_data)
        print(f"🔧 REGISTRATION DEBUG - Device created with ID: {device_id}")
        print(f"✅ Device registered: {device_data['name']} ({device_id})")
        
        # Create audit log for user registration
        audit_data = {
            "action": "User Registration",
            "user": data.email,
            "device": device_data['name'],
            "status": "success",
            "ip_address": client_ip,
            "details": f"New user registered: {data.name} with device {device_data['name']}",
            "user_id": user_id,
            "device_id": device_id,
            "metadata": {
                "email": data.email,
                "organization": data.organization,
                "platform": device_info['platform'],
                "browser": device_info['browser']
            }
        }
        
        audit_id = await FirebaseService.create_audit_log(audit_data)
        print(f"✅ Audit log created: {audit_id}")
        
        # Get the created user
        created_user = await FirebaseService.get_user_by_id(user_id)
        print(f"✅ User registered in Firebase: {data.email}")
        
        return UserResponse(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/login", response_model=TokenResponse)
async def login_user(data: LoginRequest, request: Request):
    """
    Login endpoint using Firebase Firestore for user lookup.
    Also registers/updates device information and supports demo credentials for testing.
    """
    try:
        user_id = None
        user_email = data.email
        
        # First check demo credentials for testing
        demo_users = {
            "test@test.com": {
                "id": "demo-user-123",
                "email": "test@test.com", 
                "name": "Demo User",
                "password": "password123",
                "role": "user",
                "is_active": True
            },
            "demo@clipvault.com": {
                "id": "demo-user-456",
                "email": "demo@clipvault.com",
                "name": "ClipVault Demo",
                "password": "demo123", 
                "role": "admin",
                "is_active": True
            }
        }
        
        # Check if it's a demo user first
        if data.email in demo_users:
            user = demo_users[data.email]
            if data.password == user["password"]:
                print(f"✅ Demo login successful for {data.email}")
                user_id = user["id"]
                access_token = create_access_token({"sub": user["id"], "email": user["email"]})
                print(f"🔑 Generated access token for user_id: {user_id}")
            else:
                print(f"❌ Demo login failed: Invalid password for {data.email}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            # Try Firebase user lookup
            try:
                firebase_user = await FirebaseService.get_user_by_email(data.email)
                if firebase_user and await FirebaseService.verify_password(data.email, data.password):
                    print(f"✅ Firebase login successful for {data.email}")
                    user_id = firebase_user["id"]
                    access_token = create_access_token({"sub": firebase_user["id"], "email": firebase_user["email"]})
                else:
                    print(f"❌ Firebase login failed: Invalid credentials for {data.email}")
                    raise HTTPException(status_code=401, detail="Invalid credentials")
            except Exception as e:
                print(f"⚠️ Firebase login attempt failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # If we get here, login was successful - now register/update device
        if user_id:
            print(f"🔧 Starting device registration for user_id: {user_id}")
            # Get client IP and User-Agent for device detection
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "unknown")
            print(f"🌐 Client IP: {client_ip}, User-Agent: {user_agent[:100]}...")
            
            # Extract device information from User-Agent
            device_info = extract_device_info(user_agent)
            print(f"📱 Device info extracted: {device_info}")
            
            # Check if this device already exists for this user
            existing_devices = await FirebaseService.get_user_devices(user_id)
            print(f"📋 Found {len(existing_devices)} existing devices for user")
            device_signature = f"{device_info['platform']}-{device_info['browser']}-{client_ip}"
            
            existing_device = None
            for device in existing_devices:
                device_meta = device.get('metadata', {})
                if device_meta.get('device_signature') == device_signature:
                    existing_device = device
                    break
            
            if existing_device:
                # Update existing device's last_seen and online status
                await FirebaseService.update_device_activity(existing_device['id'], user_id)
                print(f"✅ Updated existing device activity: {existing_device['name']}")
                
                # Create audit log for existing device login
                audit_data = {
                    "action": "User Login",
                    "user": user_email,
                    "device": existing_device['name'],
                    "status": "success",
                    "ip_address": client_ip,
                    "details": f"User logged in from existing device: {existing_device['name']}",
                    "user_id": user_id,
                    "device_id": existing_device['id'],
                    "metadata": {
                        "email": user_email,
                        "platform": device_info['platform'],
                        "browser": device_info['browser'],
                        "device_type": device_info['device_type'],
                        "existing_device": True
                    }
                }
                
                audit_id = await FirebaseService.create_audit_log(audit_data)
                print(f"✅ Existing device login audit log created: {audit_id}")
            else:
                # Create new device entry for this login
                device_data = {
                    "name": device_info['device_name'],
                    "device_type": device_info['device_type'],
                    "platform": device_info['platform'], 
                    "browser": device_info['browser'],
                    "user_id": user_id,
                    "ip_address": client_ip,
                    "is_trusted": False,  # New devices need to be trusted manually
                    "is_online": True,
                    "user_agent": user_agent,
                    "metadata": {
                        "device_signature": device_signature,
                        "login_device": True,
                        "source": "user_login",
                        "os_version": device_info.get('os_version', 'Unknown'),
                        "browser_version": device_info.get('browser_version', 'Unknown'),
                        "first_login": datetime.utcnow().isoformat()
                    }
                }
                
                device_id = await FirebaseService.create_device(device_data)
                print(f"✅ New device registered on login: {device_data['name']} ({device_id})")
                
                # Create audit log for new device login
                audit_data = {
                    "action": "New Device Login",
                    "user": user_email,
                    "device": device_data['name'],
                    "status": "success",
                    "ip_address": client_ip,
                    "details": f"User logged in from new device: {device_data['name']}",
                    "user_id": user_id,
                    "device_id": device_id,
                    "metadata": {
                        "email": user_email,
                        "platform": device_info['platform'],
                        "browser": device_info['browser'],
                        "device_type": device_info['device_type']
                    }
                }
                
                audit_id = await FirebaseService.create_audit_log(audit_data)
                print(f"✅ New device audit log created: {audit_id}")
            
            return TokenResponse(access_token=access_token, token_type="bearer")
        
        # If we get here, something went wrong
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/logout")
async def logout_user(request: Request):
    """
    Logout endpoint that updates device status to offline.
    """
    try:
        # Get user ID from JWT token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
                
                if user_id:
                    # Get client info for device identification
                    client_ip = request.client.host if request.client else "unknown"
                    user_agent = request.headers.get("User-Agent", "unknown")
                    device_info = extract_device_info(user_agent)
                    device_signature = f"{device_info['platform']}-{device_info['browser']}-{client_ip}"
                    
                    # Find and update the current device to offline
                    existing_devices = await FirebaseService.get_user_devices(user_id)
                    for device in existing_devices:
                        device_meta = device.get('metadata', {})
                        if device_meta.get('device_signature') == device_signature:
                            await FirebaseService.update_device_status(device['id'], False)
                            print(f"✅ Device set to offline on logout: {device['name']}")
                            break
                    
                    # Create audit log for logout
                    audit_data = {
                        "action": "User Logout",
                        "user": payload.get("email", "unknown"),
                        "device": device_info['device_name'],
                        "status": "success",
                        "ip_address": client_ip,
                        "details": f"User logged out from device: {device_info['device_name']}",
                        "user_id": user_id,
                        "metadata": {
                            "platform": device_info['platform'],
                            "browser": device_info['browser']
                        }
                    }
                    
                    await FirebaseService.create_audit_log(audit_data)
                    print(f"✅ Logout audit log created for user: {user_id}")
                    
            except jwt.ExpiredSignatureError:
                print("⚠️ Logout attempt with expired token")
            except jwt.InvalidTokenError:
                print("⚠️ Logout attempt with invalid token")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        print(f"❌ Logout error: {e}")
        return {"message": "Logged out successfully"}  # Always return success for logout

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: Request):
    # Implement refresh logic if using refresh tokens
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/me", response_model=UserResponse)
async def get_me(request: Request):
    """
    Get current user info from JWT token, supporting both Firebase and demo users.
    """
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization header")
        
        token = auth_header.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        
        # Check if it's a demo user
        if user_id in ["demo-user-123", "demo-user-456"]:
            demo_user = {
                "id": user_id,
                "email": email,
                "name": "Demo User" if email == "test@test.com" else "ClipVault Demo",
                "role": "user" if email == "test@test.com" else "admin",
                "is_active": True,
                "organization": "Demo Organization"
            }
            return UserResponse(**demo_user)
        
        # Try to get user from Firebase
        try:
            firebase_user = await FirebaseService.get_user_by_id(user_id)
            if firebase_user:
                return UserResponse(**firebase_user)
        except Exception as e:
            print(f"⚠️ Firebase user lookup failed: {e}")
        
        # Fallback: create user response from token data
        fallback_user = {
            "id": user_id,
            "email": email,
            "name": email.split("@")[0].title(),
            "role": "user",
            "is_active": True,
            "organization": "ClipVault"
        }
        return UserResponse(**fallback_user)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"❌ Get user error: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/current-device")
async def get_current_device(request: Request):
    """
    Get information about the current device/session.
    """
    try:
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        device_info = extract_device_info(user_agent)
        
        # Get user ID if authenticated
        user_id = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = payload.get("sub")
            except:
                pass
        
        return {
            "device_info": device_info,
            "ip_address": client_ip,
            "user_agent": user_agent,
            "is_authenticated": user_id is not None,
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"❌ Error getting current device info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get device information")

# Helper to create JWT

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def extract_device_info(user_agent: str) -> dict:
    """
    Extract detailed device information from User-Agent string.
    Returns device name, type, platform, browser details, and OS version.
    """
    if not user_agent or user_agent == "unknown":
        return {
            "device_name": "Unknown Device",
            "device_type": "desktop",
            "platform": "Unknown",
            "browser": "Unknown",
            "os_version": "Unknown"
        }
    
    user_agent_lower = user_agent.lower()
    
    # Detect platform/OS with version
    platform = "Unknown"
    os_version = "Unknown"
    
    if "windows nt 10" in user_agent_lower:
        platform = "Windows"
        os_version = "10/11"
    elif "windows nt 6.3" in user_agent_lower:
        platform = "Windows"
        os_version = "8.1"
    elif "windows nt 6.2" in user_agent_lower:
        platform = "Windows"
        os_version = "8"
    elif "windows nt 6.1" in user_agent_lower:
        platform = "Windows"
        os_version = "7"
    elif "windows" in user_agent_lower:
        platform = "Windows"
        os_version = "Unknown"
    elif "mac os x 10_15" in user_agent_lower or "mac os x 10.15" in user_agent_lower:
        platform = "macOS"
        os_version = "Catalina"
    elif "mac os x 11_" in user_agent_lower or "mac os x 11." in user_agent_lower:
        platform = "macOS"
        os_version = "Big Sur"
    elif "mac os x 12_" in user_agent_lower or "mac os x 12." in user_agent_lower:
        platform = "macOS"
        os_version = "Monterey"
    elif "mac os x 13_" in user_agent_lower or "mac os x 13." in user_agent_lower:
        platform = "macOS"
        os_version = "Ventura"
    elif "mac os x 14_" in user_agent_lower or "mac os x 14." in user_agent_lower:
        platform = "macOS"
        os_version = "Sonoma"
    elif "macintosh" in user_agent_lower or "mac os" in user_agent_lower:
        platform = "macOS"
        os_version = "Unknown"
    elif "ubuntu" in user_agent_lower:
        platform = "Ubuntu"
    elif "linux" in user_agent_lower:
        platform = "Linux"
    elif "android 13" in user_agent_lower:
        platform = "Android"
        os_version = "13"
    elif "android 12" in user_agent_lower:
        platform = "Android"
        os_version = "12"
    elif "android 11" in user_agent_lower:
        platform = "Android"
        os_version = "11"
    elif "android 10" in user_agent_lower:
        platform = "Android"
        os_version = "10"
    elif "android" in user_agent_lower:
        platform = "Android"
        os_version = "Unknown"
    elif "iphone os 17_" in user_agent_lower:
        platform = "iOS"
        os_version = "17"
    elif "iphone os 16_" in user_agent_lower:
        platform = "iOS"
        os_version = "16"
    elif "iphone os 15_" in user_agent_lower:
        platform = "iOS"
        os_version = "15"
    elif "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        platform = "iOS"
        os_version = "Unknown"
    
    # Detect device type with more accuracy
    device_type = "desktop"
    if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
        device_type = "mobile"
    elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        device_type = "tablet"
    elif "tv" in user_agent_lower or "smart" in user_agent_lower:
        device_type = "tv"
    
    # Detect browser with version
    browser = "Unknown"
    browser_version = "Unknown"
    
    if "edg/" in user_agent_lower:
        browser = "Edge"
        try:
            browser_version = user_agent.split("Edg/")[1].split()[0]
        except:
            pass
    elif "chrome/" in user_agent_lower and "edg" not in user_agent_lower:
        browser = "Chrome"
        try:
            browser_version = user_agent.split("Chrome/")[1].split()[0]
        except:
            pass
    elif "firefox/" in user_agent_lower:
        browser = "Firefox"
        try:
            browser_version = user_agent.split("Firefox/")[1].split()[0]
        except:
            pass
    elif "safari/" in user_agent_lower and "chrome" not in user_agent_lower:
        browser = "Safari"
        try:
            browser_version = user_agent.split("Version/")[1].split()[0]
        except:
            pass
    elif "opera" in user_agent_lower:
        browser = "Opera"
    
    # Generate comprehensive device name
    device_name = f"{platform}"
    if os_version != "Unknown":
        device_name += f" {os_version}"
    
    if browser != "Unknown":
        device_name += f" - {browser}"
        if browser_version != "Unknown":
            device_name += f" {browser_version.split('.')[0]}"  # Just major version
    
    if device_type == "mobile":
        device_name = f"Mobile {device_name}"
    elif device_type == "tablet":
        device_name = f"Tablet {device_name}"
    elif device_type == "tv":
        device_name = f"Smart TV {device_name}"
    
    return {
        "device_name": device_name,
        "device_type": device_type,
        "platform": platform,
        "browser": browser,
        "browser_version": browser_version,
        "os_version": os_version
    }
