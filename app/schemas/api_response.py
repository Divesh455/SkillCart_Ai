from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[Any] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation completed successfully",
                "data": {},
                "errors": None,
                "timestamp": "2026-07-13T10:45:00Z"
            }
        }
    )
        
def success_response(data: Any = None, message: str = "Success") -> ApiResponse:
    return ApiResponse(success=True, message=message, data=data, errors=None)

def error_response(errors: Any = None, message: str = "Error occurred") -> ApiResponse:
    return ApiResponse(success=False, message=message, data=None, errors=errors)
