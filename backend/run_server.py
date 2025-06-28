#!/usr/bin/env python3
"""
Simple server runner for ClipVault Backend
"""
import uvicorn
from app import app

if __name__ == "__main__":
    print("🚀 Starting ClipVault Backend Server...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=False
    )
