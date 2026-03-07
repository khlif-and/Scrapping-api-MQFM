import logging
from typing import Any, Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from otp.application.dto import GenerateOTPRequest, VerifyOTPRequest
from otp.infrastructure.cache_adapter import OTPCacheAdapter
from otp.infrastructure.email_adapter import OTPEmailAdapter
from otp.application.use_case import GenerateOTPUseCase, VerifyOTPUseCase

logger = logging.getLogger(__name__)
router = APIRouter()


class OTPResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


@router.post("/otp/generate", response_model=OTPResponse)
def generate_otp(request: GenerateOTPRequest, background_tasks: BackgroundTasks):
    try:
        cache = OTPCacheAdapter()
        email_sender = OTPEmailAdapter()
        use_case = GenerateOTPUseCase(cache=cache, email_sender=email_sender)
        result = use_case.execute(request.email)
        return OTPResponse(**result)
    except Exception as e:
        logger.error(f"Error generating OTP: {e}")
        return OTPResponse(success=False, message=str(e))


@router.post("/otp/verify", response_model=OTPResponse)
def verify_otp(request: VerifyOTPRequest):
    try:
        cache = OTPCacheAdapter()
        use_case = VerifyOTPUseCase(cache=cache)
        result = use_case.execute(request.email, request.otp_code)
        return OTPResponse(**result)
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return OTPResponse(success=False, message=str(e))
