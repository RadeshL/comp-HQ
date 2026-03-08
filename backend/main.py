import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from database import create_tables
from api.component_routes import router as component_router
from api.report_routes import router as report_router
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="comp-HQ API",
    description="AI-Powered Component Sourcing Assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(component_router)
app.include_router(report_router)

# Serve static files (for reports)
if not os.path.exists(settings.OUTPUT_DIR):
    os.makedirs(settings.OUTPUT_DIR)

app.mount("/reports", StaticFiles(directory=settings.OUTPUT_DIR), name="reports")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to comp-HQ API",
        "version": "1.0.0",
        "description": "AI-Powered Component Sourcing Assistant",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "comp-HQ API is running",
        "version": "1.0.0"
    }

@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "name": "comp-HQ API",
        "version": "1.0.0",
        "description": "AI-Powered Component Sourcing Assistant",
        "features": [
            "Component search across multiple retailers",
            "Product ranking with AI-powered scoring",
            "Product selection management",
            "Procurement report generation",
            "Word document export"
        ],
        "endpoints": {
            "components": "/api/components",
            "reports": "/api/reports",
            "documentation": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting comp-HQ API server on {settings.API_HOST}:{settings.API_PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level="info"
    )
