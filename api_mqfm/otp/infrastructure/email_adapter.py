import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from otp.domain.port import OTPEmailPort

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


class OTPEmailAdapter(OTPEmailPort):
    def send_otp(self, email: str, otp_code: str) -> None:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Kode Keamanan OTP - MQFM Apps'
            msg['From'] = f"MQFM Apps <{SMTP_EMAIL}>"
            msg['To'] = email

            text = f"Kode OTP Anda adalah {otp_code}.\n\nBerlaku selama 5 menit. Jangan berikan kode ini ke siapapun."

            template_path = os.path.join(os.path.dirname(__file__), "..", "..", "templates", "email_otp.html")
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
