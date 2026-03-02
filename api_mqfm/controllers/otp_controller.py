import logging
import requests
from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.otp_model import GenerateOTPRequest, VerifyOTPRequest, OTPResponse
from services.otp_service import OTPService

router = APIRouter()
logger = logging.getLogger(__name__)

def send_whatsapp_node(phone_number: str, message: str):
    try:
        url = "http://localhost:3000/send"
        data = {
            "phone": phone_number,
            "message": message
        }
        response = requests.post(url, json=data)
        if response.status_code != 200:
            logger.error(f"NodeJS Baileys Error: {response.text}")
    except Exception as e:
        logger.error(f"Gagal koneksi ke NodeJS Baileys: {e}")

@router.post("/otp/generate", response_model=OTPResponse)
def generate_otp(request: GenerateOTPRequest, background_tasks: BackgroundTasks):
    try:
        otp_code = OTPService.generate_otp(request.phone_number)
        pesan_wa = f"*[MQFM API]*\nKode OTP Anda adalah *{otp_code}*.\n\nBerlaku selama 5 menit. Jangan berikan kode ini ke siapapun."
        
        background_tasks.add_task(send_whatsapp_node, request.phone_number, pesan_wa)
        
        return OTPResponse(
            message=f"Kode OTP {otp_code} berhasil digenerate dan dikirim.",
            success=True
        )
    except Exception as e:
        logger.error(f"Error generating OTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/otp/verify", response_model=OTPResponse)
def verify_otp(request: VerifyOTPRequest):
    try:
        is_valid = OTPService.verify_otp(request.phone_number, request.otp_code)
        if is_valid:
            return OTPResponse(message="OTP Valid! Verifikasi berhasil.", success=True)
        else:
            raise HTTPException(status_code=400, detail="OTP tidak valid atau sudah kedaluwarsa.")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))
