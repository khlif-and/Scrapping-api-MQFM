import logging
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, BackgroundTasks

from api_requests.otp_request import GenerateOTPRequest, VerifyOTPRequest
from resources.otp_resource import OTPResource
from services.otp_service import OTPService

load_dotenv()

router = APIRouter()
logger = logging.getLogger(__name__)

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_email_otp(email_addr: str, otp_code: str):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Kode Keamanan OTP - MQFM Apps'
        msg['From'] = f"MQFM Apps <{SMTP_EMAIL}>"
        msg['To'] = email_addr

        text = f"Kode OTP Anda adalah {otp_code}.\n\nBerlaku selama 5 menit. Jangan berikan kode ini ke siapapun."
        
        template_path = os.path.join(os.path.dirname(__file__), "..", "templates", "email_otp.html")
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()
            
        html = html_template.format(otp_code=otp_code)

        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        logger.error(f"Gagal mengirim email OTP: {e}")

@router.post("/otp/generate", response_model=OTPResource)
def generate_otp(request: GenerateOTPRequest, background_tasks: BackgroundTasks):
    try:
        otp_entity = OTPService.generate_otp(request.email)
        
        background_tasks.add_task(send_email_otp, otp_entity.email, otp_entity.otp_code)
        
        return OTPResource.success_response(
            message=f"Kode OTP berhasil digenerate dan dikirim ke {otp_entity.email}."
        )
    except Exception as e:
        logger.error(f"Error generating OTP: {e}")
        return OTPResource.error_response(message=str(e))

@router.post("/otp/verify", response_model=OTPResource)
def verify_otp(request: VerifyOTPRequest):
    try:
        is_valid = OTPService.verify_otp(request.email, request.otp_code)
        if is_valid:
            return OTPResource.success_response(message="OTP Valid! Verifikasi berhasil.")
        else:
            return OTPResource.error_response(message="OTP tidak valid atau sudah kedaluwarsa.")
    except Exception as e:
        logger.error(f"Error verifying OTP: {e}")
        return OTPResource.error_response(message=str(e))
