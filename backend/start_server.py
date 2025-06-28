#!/usr/bin/env python3
"""
Start script for ClipVault Backend
"""
import sys
import os
import subprocess

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # Run the uvicorn server
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", "8001", 
        "--reload"
    ]
    
    print("🚀 Starting ClipVault Backend...")
    print(f"📂 Working directory: {current_dir}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📡 Command: {' '.join(cmd)}")
    
    subprocess.run(cmd, cwd=current_dir)