from pydantic import BaseModel

class GenerateOTPRequest(BaseModel):
    phone_number: str

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp_code: str

class OTPResponse(BaseModel):
    message: str
    success: bool
