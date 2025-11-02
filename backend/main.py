"""
SOAP Note Generation Backend - Main Application
A production-level FastAPI backend for medical SOAP note generation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import configuration
from configs.settings import CORS_ORIGINS

# Import routes
from routes.visit_routes import router as visit_router
from routes.soap_routes import router as soap_router
from routes.system_routes import router as system_router

# Import services
from services.cleanup import cleanup_resources
from services.model_manager import model_manager  # This initializes models on import

# Import logger
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events (startup and shutdown)."""
    # Startup code
    logger.info("FastAPI application starting up")
    logger.info("Models initialized and ready")
    yield
    # Shutdown code
    logger.info("FastAPI shutdown event triggered")
    cleanup_resources()


# Create FastAPI app
app = FastAPI(
    title="SOAP Note Generator API",
    description="AI-powered medical SOAP note generation from audio recordings",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(visit_router, tags=["Visits"])
app.include_router(soap_router, tags=["SOAP Notes"])
app.include_router(system_router, tags=["System"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "SOAP Note Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": True,
        "device": model_manager.device
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
