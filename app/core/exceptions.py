from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.api_response import error_response

class SkillCartException(Exception):
    """Base exception for all SkillCart AI errors."""
    def __init__(self, message: str, status_code: int = 500, errors: any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors

class DocumentParsingException(SkillCartException):
    """Raised when document parsing fails (invalid formats, corrupted files, etc.)."""
    def __init__(self, message: str, errors: any = None):
        super().__init__(message, status_code=400, errors=errors)

class LLMProviderException(SkillCartException):
    """Raised when LLM calls fail (timeouts, rate limits, provider errors, validation failures)."""
    def __init__(self, message: str, errors: any = None):
        super().__init__(message, status_code=502, errors=errors)

class SchemaValidationException(SkillCartException):
    """Raised when the response models fail validation even after retries."""
    def __init__(self, message: str, errors: any = None):
        super().__init__(message, status_code=422, errors=errors)

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SkillCartException)
    async def skillcart_exception_handler(request: Request, exc: SkillCartException):
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(errors=exc.errors, message=exc.message).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error_response(
                errors=exc.errors(), 
                message="Request validation failed"
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=error_response(
                errors=str(exc),
                message="An unexpected error occurred"
            ).model_dump()
        )
