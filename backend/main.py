"""
ClipVault Backend Application Entry Point

Main FastAPI application with Firebase Firestore and Redis integration.
This is the main application file that sets up all routes, middleware, and services.
"""

from fastapi import FastAPI, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from app.services.firebase_service import FirebaseService
from app.services.redis_service import RedisService
from app.websocket_manager import WebSocketManager

# Import routers
from app.routers import auth, users, devices, clipboard, security, audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    print("🔥 Initializing Firebase service...")
    await FirebaseService.initialize()
    print("📡 Initializing Redis service...")
    await RedisService.initialize()
    print("🚀 ClipVault Backend Started Successfully")
    
    yield
    
    # Shutdown
    print("🔥 Closing Firebase service...")
    await FirebaseService.close()
    print("📡 Closing Redis service...")
    await RedisService.close()
    print("👋 ClipVault Backend Stopped")

def create_app() -> FastAPI:
    """
    Factory function to create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="ClipVault API",
        description="Secure Clipboard Management Backend with Firebase & Redis",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",    # React dev server (CRA)
            "http://localhost:5173",    # Vite dev server
            "http://localhost:5174",    # Alternative Vite port
            "http://localhost:5175",    # Alternative Vite port
            "http://localhost:5176",    # Alternative Vite port
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176",
            "https://clipy-pi.vercel.app",  # Your Vercel frontend
            "https://*.vercel.app",         # All Vercel apps
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Initialize WebSocket Manager
    websocket_manager = WebSocketManager()

    # Include API routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/users", tags=["Users"])
    app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
    app.include_router(clipboard.router, prefix="/api/clipboard", tags=["Clipboard"])
    app.include_router(security.router, prefix="/api/security", tags=["Security"])
    app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint with basic API information."""
        return {
            "message": "ClipVault API is running",
            "version": "2.0.0",
            "backend": "Firebase Firestore + Redis",
            "docs": "/docs",
            "health": "/health"
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint for monitoring and load balancers."""
        try:
            # Basic health check - could be expanded to check Firebase/Redis connectivity
            return {
                "status": "healthy",
                "service": "ClipVault Backend",
                "version": "2.0.0",
                "backend": "Firebase + Redis",
                "timestamp": "2025-06-28T00:00:00Z"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service unhealthy: {str(e)}"
            )

    @app.websocket("/ws/{client_id}")
    async def websocket_endpoint(websocket: WebSocket, client_id: str):
        """
        WebSocket endpoint for real-time clipboard synchronization.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
        """
        await websocket_manager.connect(websocket, client_id)
        try:
            while True:
                data = await websocket.receive_text()
                # Echo back for now - can be extended for clipboard sync
                await websocket_manager.send_personal_message(
                    f"Clipboard sync: {data}", 
                    client_id
                )
        except WebSocketDisconnect:
            websocket_manager.disconnect(client_id)

    return app

# Create the application instance
app = create_app()

def run_server():
    """
    Run the application server with uvicorn.
    Used for development and direct execution.
    """
    uvicorn.run(
        "__main__:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        reload=True,
        log_level="info",
        access_log=True,
        use_colors=True
    )

if __name__ == "__main__":
    run_server()
