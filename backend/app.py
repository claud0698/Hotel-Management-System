"""
Kos Management Dashboard - FastAPI Backend Application
Supports SQLite (development), PostgreSQL (production), and Google Cloud SQL (GCP)
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional

from models import Base, db
from routes import auth_router, users_router, rooms_router, tenants_router, payments_router, expenses_router, dashboard_router

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./kos.db')

# Create engine and session factory
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup/shutdown"""
    # Startup
    Base.metadata.create_all(bind=engine)
    print(f"Database: {DATABASE_URL}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    yield
    # Shutdown
    pass


def create_app():
    """Application factory for FastAPI app creation"""
    app = FastAPI(
        title="Kos Management API",
        description="REST API for managing tenant properties (Kos) in Indonesia",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json"
    )

    # CORS Configuration - allow all origins for testing (disable for production)
    cors_origins = os.getenv('CORS_ORIGINS', '*')  # Allow all origins for testing

    if cors_origins == '*':
        # Allow all origins for testing
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        # Restrict to specific origins in production
        origins = [origin.strip() for origin in cors_origins.split(',')]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Health check endpoint
    @app.get('/health')
    async def health():
        """Health check endpoint for deployment monitoring"""
        return {
            'status': 'ok',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'database': 'sqlite' if 'sqlite' in DATABASE_URL else 'postgresql',
            'timestamp': datetime.utcnow().isoformat()
        }

    # API root endpoint
    @app.get('/api')
    async def api_root():
        """API root endpoint with version info"""
        return {
            'message': 'Kos Management API',
            'version': '1.0.0',
            'status': 'active',
            'docs': '/api/docs',
            'openapi': '/api/openapi.json'
        }

    # Include routers
    app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users_router.router, prefix="/api/users", tags=["Users"])
    app.include_router(rooms_router.router, prefix="/api/rooms", tags=["Rooms"])
    app.include_router(tenants_router.router, prefix="/api/tenants", tags=["Tenants"])
    app.include_router(payments_router.router, prefix="/api/payments", tags=["Payments"])
    app.include_router(expenses_router.router, prefix="/api/expenses", tags=["Expenses"])
    app.include_router(dashboard_router.router, prefix="/api/dashboard", tags=["Dashboard"])

    # Error handlers
    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        return JSONResponse(
            status_code=404,
            content={"error": "Endpoint not found"}
        )

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv('PORT', 8001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="info"
    )
