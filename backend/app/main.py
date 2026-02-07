"""
Stratify AI - Main Application
Entry point for FastAPI backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routes import auth_routes, analysis_routes

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Global Multi-Factor Influence Intelligence Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS - Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """
    Initialize database on startup
    Creates all tables if they don't exist
    """
    print("Initializing database...")
    init_db()
    print("Database initialized successfully")


@app.get("/")
def root():
    """
    Root endpoint - API health check
    """
    return {
        "message": "Welcome to Stratify AI",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "auth": "/auth",
            "analysis": "/analysis"
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "service": "Stratify AI Backend",
        "timestamp": "2024-02-07"
    }


# Include routers
app.include_router(auth_routes.router)
app.include_router(analysis_routes.router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler
    Returns proper error response with CORS headers
    """
    import traceback
    if settings.DEBUG:
        traceback.print_exc()
    
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in settings.ALLOWED_ORIGINS:
        headers["access-control-allow-origin"] = origin
        headers["access-control-allow-credentials"] = "true"
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "An internal error occurred",
            "detail": str(exc) if settings.DEBUG else "Internal server error"
        },
        headers=headers
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
