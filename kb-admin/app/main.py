"""
KB-Admin FastAPI Application
Main entry point for the Knowledge Base Management microservice
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import test_connection as test_db_connection
from app.redis_client import test_redis_connection
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KB-Admin Service",
    description="Knowledge Base Management Microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Run startup checks and initialization
    """
    logger.info(f"Starting {settings.SERVICE_NAME} service...")

    # Test database connection
    if test_db_connection():
        logger.info("✓ MySQL connection successful")
    else:
        logger.error("✗ MySQL connection failed")
        raise Exception("Failed to connect to MySQL")

    # Test Redis connection
    if test_redis_connection():
        logger.info("✓ Redis connection successful")
    else:
        logger.error("✗ Redis connection failed")
        raise Exception("Failed to connect to Redis")

    logger.info(f"✓ {settings.SERVICE_NAME} service started successfully on port {settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    logger.info(f"Shutting down {settings.SERVICE_NAME} service...")


@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "status": "running",
        "message": "Knowledge Base Management Service"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    db_status = test_db_connection()
    redis_status = test_redis_connection()

    if not db_status or not redis_status:
        raise HTTPException(status_code=503, detail="Service unhealthy")

    return {
        "status": "healthy",
        "mysql": "connected" if db_status else "disconnected",
        "redis": "connected" if redis_status else "disconnected"
    }


# Import and include routers
from app.api import kb_routes, document_routes, learned_knowledge_routes
app.include_router(kb_routes.router, prefix="/api/kb", tags=["Knowledge Base"])
app.include_router(document_routes.router, prefix="/api/kb", tags=["Documents"])
app.include_router(learned_knowledge_routes.router, prefix="/api/learning", tags=["Self-Learning"])
