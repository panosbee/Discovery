"""
Medical Discovery & Hypothesis Engine - Main FastAPI Application
A microservice for generating innovative medical hypotheses using AI-powered multi-agent systems
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from loguru import logger
import sys
from datetime import datetime

from medical_discovery.config import settings
from medical_discovery.api.routes import hypothesis
from medical_discovery.api.schemas.hypothesis import ErrorResponse


# Configure loguru logger
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level=settings.log_level
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize MongoDB connection
    try:
        from medical_discovery.data.mongo.client import mongodb_client
        await mongodb_client.connect()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        logger.warning("Continuing without MongoDB (using in-memory storage)")
    
    # TODO: Initialize Redis connection
    # TODO: Initialize Vector DB connection
    # TODO: Warm up AI models if needed
    
    logger.success("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Close MongoDB connection
    try:
        from medical_discovery.data.mongo.client import mongodb_client
        await mongodb_client.disconnect()
    except Exception as e:
        logger.error(f"Error closing MongoDB: {str(e)}")
    
    # TODO: Close Redis connection
    # TODO: Cleanup resources
    logger.success("Application shutdown complete")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered medical hypothesis generation across all medical domains",
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://medresearch-ai.org"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="ValidationError",
            message="Invalid request data",
            details={"errors": exc.errors()},
            timestamp=datetime.utcnow()
        ).model_dump(mode='json')  # Use mode='json' to serialize datetime
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"exception": str(exc)} if settings.debug else None,
            timestamp=datetime.utcnow()
        ).model_dump(mode='json')  # Use mode='json' to serialize datetime
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from medical_discovery.data.mongo.client import mongodb_client
    
    # Check MongoDB connection
    mongodb_status = await mongodb_client.is_connected()
    
    return {
        "status": "healthy" if mongodb_status else "degraded",
        "version": settings.app_version,
        "timestamp": datetime.utcnow(),
        "mongodb_connected": mongodb_status,
        "intelligence_modules": ["EvidenceScorer", "QueryExpander", "EvidenceDeduplicator"],
        "services": {
            "api": True,
            "mongodb": mongodb_status,
            "redis": False,     # TODO: Check actual connection
            "qdrant": False,    # TODO: Check actual connection
        }
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Medical Discovery & Hypothesis Engine",
        "docs": "/docs" if settings.debug else None,
        "health": "/health",
        "supported_domains": settings.supported_domains
    }


# Include routers
app.include_router(hypothesis.router, prefix="/api/v1", tags=["Hypotheses"])


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "medical_discovery.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
