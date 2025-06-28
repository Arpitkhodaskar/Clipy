#!/usr/bin/env python3
"""
Test Server for ClipVault Backend
"""
import sys
import os
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import services
from app.services.firebase_service import FirebaseService
from app.services.redis_service import RedisService

# Import routers
from app.routers import auth, users, devices, clipboard, security, audit

async def startup():
    """Startup tasks"""
    print("🔥 Initializing Firebase service...")
    await FirebaseService.initialize()
    print("📡 Initializing Redis service...")
    await RedisService.initialize()
    print("🚀 ClipVault Backend Started Successfully")

def create_test_app():
    app = FastAPI(
        title="ClipVault API",
        description="Secure Clipboard Management Backend with Firebase & Redis",
        version="2.0.0"
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["Users"])
    app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
    app.include_router(clipboard.router, prefix="/api/clipboard", tags=["Clipboard"])
    app.include_router(security.router, prefix="/api/security", tags=["Security"])
    app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "ClipVault Backend",
            "version": "2.0.0",
            "backend": "Firebase + Redis",
            "timestamp": "2025-06-29T00:00:00Z"
        }

    return app

if __name__ == "__main__":
    # Initialize services
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(startup())
    
    # Create and run app
    app = create_test_app()
    
    print("🚀 Starting server on http://127.0.0.1:8001")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
