import time
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limiting import RateLimitingMiddleware
from app.api.v1.router import api_router

# Setup application-wide logging
setup_logging()
logger = logging.getLogger("app.main")


def create_app() -> FastAPI:
    """
    Application factory for the FastAPI backend.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise Analytics API serving COVID-19 dashboards and operations.",
        docs_url=settings.DOCS_URL if settings.DEBUG else None,
        redoc_url=settings.REDOC_URL if settings.DEBUG else None,
    )

    # ── Register Middlewares ──
    # 1. Request ID (Ensures all logs for a request share a UUID)
    app.add_middleware(RequestIDMiddleware)
    
    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 3. Rate Limiting Middleware (100 req/min per IP)
    app.add_middleware(RateLimitingMiddleware)
    
    # 4. Latency and HTTP request logging middleware
    app.add_middleware(LoggingMiddleware)

    # ── Exception Handlers ──
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        logger.error(f"HTTP exception occurred: {exc.detail} (Status: {exc.status_code})")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "status_code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Request validation failed: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error in request parameters or body.",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error(f"Database error occurred: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "A database operation error occurred. Contact system administration."
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.critical(f"Unhandled system exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected server error occurred."},
        )

    # ── Include Routers ──
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode.")

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info(f"Shutting down {settings.APP_NAME}.")

    return app


app = create_app()
