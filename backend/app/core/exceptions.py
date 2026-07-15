import logging
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

logger = logging.getLogger("aegisai.exceptions")

class AegisException(Exception):
    """Base exception class for AegisAI."""
    def __init__(self, message: str, status_code: int = HTTP_500_INTERNAL_SERVER_ERROR) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class DatabaseException(AegisException):
    """Raised when data tier operations encounter errors."""
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=HTTP_500_INTERNAL_SERVER_ERROR)

class PolicyViolationException(AegisException):
    """Raised when a governed transaction violates compliance or security policies."""
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=HTTP_400_BAD_REQUEST)

class AuthenticationException(AegisException):
    """Raised when authorization checks or access token verification fails."""
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=HTTP_401_UNAUTHORIZED)

class EntityNotFoundException(AegisException):
    """Raised when an object or record is not found."""
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=HTTP_404_NOT_FOUND)

def register_exception_handlers(app: FastAPI) -> None:
    """
    Hooks global exception handlers into the FastAPI instance.
    """
    @app.exception_handler(AegisException)
    async def aegis_exception_handler(request: Request, exc: AegisException) -> JSONResponse:
        logger.error(f"AegisException: {exc.message} on path {request.url.path}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "message": exc.message}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.error(f"Validation error on path {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": "ValidationError", "details": exc.errors()}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.critical(f"Unhandled critical system error on path {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "InternalServerError", "message": "An unexpected critical error occurred."}
        )
