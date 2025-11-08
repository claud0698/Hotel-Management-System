"""
Comprehensive error handling and logging for Hotel Management System API
Phase 8 Task 8.3: Error Handling & Logging
"""

import logging
import json
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException


# ============== LOGGING CONFIGURATION ==============

class StructuredFormatter(logging.Formatter):
    """Structured logging formatter for better log analysis"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_data)


def setup_logging():
    """Configure logging for the application"""
    # Create logger
    logger = logging.getLogger("hotel_management")
    logger.setLevel(logging.DEBUG)

    # Remove default handlers
    logger.handlers = []

    # Console handler (INFO level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = StructuredFormatter()
    console_handler.setFormatter(console_formatter)

    # File handler (DEBUG level)
    try:
        file_handler = logging.FileHandler("logs/api.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
    except (FileNotFoundError, PermissionError):
        # If logs directory doesn't exist, just use console
        pass

    logger.addHandler(console_handler)

    # Log startup
    logger.info("Logging configured successfully")

    return logger


logger = setup_logging()


# ============== CUSTOM EXCEPTIONS ==============

class APIException(Exception):
    """Base API exception"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """Validation error"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class ResourceNotFoundException(APIException):
    """Resource not found error"""

    def __init__(self, resource: str, resource_id: int = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID {resource_id} not found"

        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND"
        )


class ConflictException(APIException):
    """Conflict error (e.g., duplicate booking)"""

    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            details=details
        )


class UnauthorizedException(APIException):
    """Unauthorized error"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )


class ForbiddenException(APIException):
    """Forbidden error (insufficient permissions)"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )


class InternalServerError(APIException):
    """Internal server error"""

    def __init__(self, message: str = "Internal server error", details: dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR",
            details=details
        )


# ============== ERROR RESPONSE SCHEMA ==============

class ErrorResponse:
    """Standard error response format"""

    @staticmethod
    def format_error(
        message: str,
        status_code: int,
        error_code: str,
        details: dict = None,
        request_id: str = None
    ) -> dict:
        """Format error response"""
        response = {
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

        if details:
            response["error"]["details"] = details

        if request_id:
            response["error"]["request_id"] = request_id

        return response


# ============== ERROR HANDLERS ==============

def create_exception_handlers(app: FastAPI):
    """Register exception handlers with FastAPI app"""

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions"""
        logger.warning(
            f"API Exception: {exc.error_code} - {exc.message}",
            extra={
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "path": request.url.path,
                "method": request.method,
                "details": exc.details
            }
        )

        error_response = ErrorResponse.format_error(
            message=exc.message,
            status_code=exc.status_code,
            error_code=exc.error_code,
            details=exc.details
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors"""
        logger.warning(
            f"Validation Error: {request.url.path}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )

        # Format validation errors
        errors = []
        for error in exc.errors():
            field_name = ".".join(str(x) for x in error["loc"][1:])
            errors.append({
                "field": field_name,
                "type": error["type"],
                "message": error["msg"]
            })

        error_response = ErrorResponse.format_error(
            message="Validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details={"errors": errors}
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            f"HTTP Exception: {exc.status_code}",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "detail": exc.detail
            }
        )

        error_code = "HTTP_ERROR"
        if exc.status_code == 401:
            error_code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            error_code = "FORBIDDEN"
        elif exc.status_code == 404:
            error_code = "NOT_FOUND"

        error_response = ErrorResponse.format_error(
            message=exc.detail or "HTTP Error",
            status_code=exc.status_code,
            error_code=error_code
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors (constraints violations)"""
        logger.error(
            f"Database Integrity Error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error": str(exc.orig)
            }
        )

        error_response = ErrorResponse.format_error(
            message="Database constraint violation",
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONSTRAINT_VIOLATION",
            details={"error": str(exc.orig)[:100]}
        )

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors"""
        logger.error(
            f"Database Error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error": str(exc)[:200]
            }
        )

        error_response = ErrorResponse.format_error(
            message="Database error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unexpected exceptions"""
        logger.error(
            f"Unexpected Exception: {type(exc).__name__}",
            exc_info=exc,
            extra={
                "path": request.url.path,
                "method": request.method,
                "exception_type": type(exc).__name__,
                "error": str(exc)[:200]
            }
        )

        error_response = ErrorResponse.format_error(
            message="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR"
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )


# ============== LOGGING MIDDLEWARE ==============

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""

    async def dispatch(self, request: Request, call_next):
        """Log request and response"""
        # Generate request ID
        request_id = request.headers.get("X-Request-ID", str(datetime.utcnow().timestamp()))

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else "unknown"
            }
        )

        # Get response
        try:
            response = await call_next(request)

            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "client": request.client.host if request.client else "unknown"
                }
            )

            return response

        except Exception as exc:
            # Log error
            logger.error(
                f"Request Error: {request.method} {request.url.path} - {str(exc)[:100]}",
                exc_info=exc,
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else "unknown"
                }
            )
            raise


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request performance"""

    async def dispatch(self, request: Request, call_next):
        """Log request performance metrics"""
        import time

        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Log slow requests (>1 second)
        if process_time > 1.0:
            logger.warning(
                f"Slow Request: {request.method} {request.url.path} took {process_time:.2f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                    "status_code": response.status_code
                }
            )

        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)

        return response


# ============== LOGGING UTILITIES ==============

def log_db_operation(operation: str, entity: str, entity_id: int = None, result: str = "success"):
    """Log database operation"""
    message = f"{operation} {entity}"
    if entity_id:
        message += f" (ID: {entity_id})"

    logger.info(
        message,
        extra={
            "operation": operation,
            "entity": entity,
            "entity_id": entity_id,
            "result": result
        }
    )


def log_auth_event(event: str, user_id: int = None, username: str = None, success: bool = True):
    """Log authentication event"""
    logger.info(
        f"Auth Event: {event}",
        extra={
            "event": event,
            "user_id": user_id,
            "username": username,
            "success": success
        }
    )


def log_payment_event(reservation_id: int, amount: float, payment_type: str, payment_method: str):
    """Log payment event"""
    logger.info(
        f"Payment Recorded: ${amount} ({payment_type})",
        extra={
            "reservation_id": reservation_id,
            "amount": amount,
            "payment_type": payment_type,
            "payment_method": payment_method
        }
    )


def log_deposit_settlement(reservation_id: int, deposit_amount: float, settlement_note: str):
    """Log deposit settlement"""
    logger.info(
        f"Deposit Settlement: ${deposit_amount}",
        extra={
            "reservation_id": reservation_id,
            "deposit_amount": deposit_amount,
            "settlement_note": settlement_note
        }
    )
