from pydantic import BaseModel
from typing import Any, Optional

class OTPResource(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

    @classmethod
    def success_response(cls, message: str, data: Any = None):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str):
        return cls(success=False, message=message)
