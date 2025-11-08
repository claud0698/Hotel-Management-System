"""
Hotel Management System - FastAPI Backend Application
Supports Supabase PostgreSQL (production)
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional

from models import Base
from database import engine, get_db
from routes import auth_router, users_router, rooms_router, payments_router, dashboard_router, guests_router, reservations_router

load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for app startup/shutdown"""
    # Startup
    from database import DATABASE_URL
    Base.metadata.create_all(bind=engine)
    print(f"Database: {DATABASE_URL}")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    yield
    # Shutdown
    pass


def create_app():
    """Application factory for FastAPI app creation"""
    app = FastAPI(
        title="Hotel Management System API",
        description="REST API for managing hotel properties, reservations, and payments",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json"
    )

    # CORS Configuration - allow all origins for testing (disable for production)
    # Must be added FIRST (before other middleware) due to middleware ordering
    cors_origins = os.getenv('CORS_ORIGINS', '*')  # Allow all origins for testing

    if cors_origins == '*':
        # Allow all origins for testing
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
        )
    else:
        # Restrict to specific origins in production
        origins = [origin.strip() for origin in cors_origins.split(',')]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["*"],
        )

    # GZip Compression Middleware - compress responses larger than 1KB
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Comprehensive health check endpoint
    @app.get('/health')
    async def health():
        """Comprehensive health check endpoint"""
        from database import DATABASE_URL, SessionLocal
        from models import User, RoomType, BookingChannel, Setting, Room, Reservation, Payment

        health_data = {
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': os.getenv('FLASK_ENV', 'development'),
            'database_type': 'postgresql' if 'postgresql' in DATABASE_URL else 'sqlite',
            'checks': {
                'database_connection': False,
                'database_tables': False,
                'initial_data': False,
                'api_server': True,
            },
            'details': {}
        }

        # Check database connection
        try:
            from sqlalchemy import text
            db = SessionLocal()
            db.execute(text('SELECT 1'))
            db.close()
            health_data['checks']['database_connection'] = True
            health_data['details']['database_status'] = 'connected'
        except Exception as e:
            health_data['status'] = 'degraded'
            health_data['details']['database_error'] = str(e)

        # Check tables
        try:
            db = SessionLocal()
            table_counts = {
                'users': db.query(User).count(),
                'room_types': db.query(RoomType).count(),
                'booking_channels': db.query(BookingChannel).count(),
                'settings': db.query(Setting).count(),
                'rooms': db.query(Room).count(),
                'reservations': db.query(Reservation).count(),
                'payments': db.query(Payment).count(),
            }
            db.close()
            health_data['checks']['database_tables'] = True
            health_data['details']['table_counts'] = table_counts
        except Exception as e:
            health_data['status'] = 'degraded'
            health_data['details']['tables_error'] = str(e)

        # Check initial data
        try:
            db = SessionLocal()
            user_count = db.query(User).count()
            room_type_count = db.query(RoomType).count()
            booking_channel_count = db.query(BookingChannel).count()
            setting_count = db.query(Setting).count()
            db.close()

            has_admin = user_count >= 1
            has_room_types = room_type_count >= 4
            has_channels = booking_channel_count >= 5
            has_settings = setting_count >= 8

            health_data['checks']['initial_data'] = (
                has_admin and has_room_types and has_channels and has_settings
            )
            health_data['details']['data_status'] = {
                'admin_user': has_admin,
                'room_types': has_room_types,
                'booking_channels': has_channels,
                'settings': has_settings,
            }
        except Exception as e:
            health_data['status'] = 'degraded'
            health_data['details']['data_error'] = str(e)

        # Determine overall status
        all_checks_passed = all(health_data['checks'].values())
        if all_checks_passed:
            health_data['status'] = 'healthy'
        elif any(health_data['checks'].values()):
            health_data['status'] = 'degraded'
        else:
            health_data['status'] = 'unhealthy'

        return health_data

    # API root endpoint
    @app.get('/api')
    async def api_root():
        """API root endpoint with version info"""
        return {
            'message': 'Hotel Management System API',
            'version': '1.0.0',
            'status': 'active',
            'docs': '/api/docs',
            'openapi': '/api/openapi.json'
        }

    # Include routers
    app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(users_router.router, prefix="/api/users", tags=["Users"])
    app.include_router(rooms_router.router, prefix="/api/rooms", tags=["Rooms"])
    app.include_router(guests_router.router, tags=["Guests"])
    app.include_router(reservations_router.router, tags=["Reservations"])
    app.include_router(payments_router.router, prefix="/api/payments", tags=["Payments"])
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
