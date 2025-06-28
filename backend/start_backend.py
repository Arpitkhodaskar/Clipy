#!/usr/bin/env python3
"""
Backend Server Starter for ClipVault
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the current directory
    backend_dir = Path(__file__).parent.absolute()
    print(f"🔧 Backend directory: {backend_dir}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    print(f"📂 Working directory: {os.getcwd()}")
    
    # Check if virtual environment is activated
    if 'venv' not in sys.executable.lower():
        print("⚠️  Virtual environment not activated")
        # Try to activate it
        venv_path = backend_dir / 'venv' / 'Scripts' / 'python.exe'
        if venv_path.exists():
            python_exe = str(venv_path)
            print(f"🐍 Using venv Python: {python_exe}")
        else:
            python_exe = sys.executable
            print(f"🐍 Using system Python: {python_exe}")
    else:
        python_exe = sys.executable
        print(f"🐍 Using activated venv Python: {python_exe}")
    
    # Start the server
    cmd = [
        python_exe, "-m", "uvicorn", 
        "app:app", 
        "--host", "127.0.0.1", 
        "--port", "8001", 
        "--reload"
    ]
    
    print("🚀 Starting ClipVault Backend Server...")
    print(f"📡 Command: {' '.join(cmd)}")
    print("🌐 Server will be available at: http://127.0.0.1:8001")
    print("📖 API docs will be available at: http://127.0.0.1:8001/docs")
    print("=" * 50)
    
    try:
        subprocess.run(cmd, cwd=backend_dir)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
