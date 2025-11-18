"""
FastAPI Main Application

Entry point for the OBE System API.
Following Clean Code: Clear structure, Dependency Injection, CORS configuration.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time
import logging

from app.core.config import settings
from app.infrastructure.database import DatabaseManager
from app.domain.exceptions import DomainException

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Application factory pattern.

    Creates and configures the FastAPI application.
    Following Factory Pattern for better testability.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API untuk Sistem Informasi Kurikulum OBE",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=settings.debug
    )

    # Configure CORS
    configure_cors(app)

    # Add middlewares
    add_middlewares(app)

    # Add exception handlers
    add_exception_handlers(app)

    # Include routers
    include_routers(app)

    # Add startup and shutdown events
    add_event_handlers(app)

    return app


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS (Cross-Origin Resource Sharing).

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    logger.info(f"CORS configured with origins: {settings.cors.origins}")


def add_middlewares(app: FastAPI) -> None:
    """
    Add custom middlewares to the application.

    Args:
        app: FastAPI application instance
    """

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """Middleware to add response time header."""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Middleware to log all requests."""
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Status: {response.status_code}")
        return response


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add custom exception handlers.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        """Handle domain-level exceptions."""
        logger.warning(f"Domain exception: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error_code": exc.error_code,
                "message": exc.message
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """Handle request validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Data tidak valid",
                "details": exc.errors()
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Terjadi kesalahan pada server"
            }
        )


def include_routers(app: FastAPI) -> None:
    """
    Include API routers.

    Args:
        app: FastAPI application instance
    """
    # Import routers here to avoid circular imports
    from app.presentation.api.v1 import kurikulum

    # Include routers
    app.include_router(
        kurikulum.router,
        prefix=f"{settings.api_v1_prefix}/kurikulum",
        tags=["Kurikulum Management"]
    )

    logger.info("✓ API routers registered")
    # TODO: Add more routers as implemented
    # app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["Authentication"])
    # app.include_router(cpl.router, prefix=f"{settings.api_v1_prefix}/cpl", tags=["CPL"])
    # app.include_router(matakuliah.router, prefix=f"{settings.api_v1_prefix}/matakuliah", tags=["Mata Kuliah"])


def add_event_handlers(app: FastAPI) -> None:
    """
    Add startup and shutdown event handlers.

    Args:
        app: FastAPI application instance
    """

    @app.on_event("startup")
    async def startup_event():
        """Execute on application startup."""
        logger.info("="*50)
        logger.info(f"Starting {settings.app_name} v{settings.app_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")
        logger.info("="*50)

        # Check database connection
        if DatabaseManager.check_database_connection():
            logger.info("✓ Database connection successful")
            db_info = DatabaseManager.get_connection_info()
            logger.info(f"  Database: {db_info['database']} @ {db_info['host']}:{db_info['port']}")
        else:
            logger.error("✗ Database connection failed!")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Execute on application shutdown."""
        logger.info("Shutting down application...")


# Create application instance
app = create_application()


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns application and database status.
    """
    db_healthy = DatabaseManager.check_database_connection()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "database": "connected" if db_healthy else "disconnected",
        "environment": settings.environment
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )
