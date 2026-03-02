import random
import logging
from redis_client import redis_client

logger = logging.getLogger(__name__)

class OTPService:
    @staticmethod
    def generate_otp(phone_number: str) -> str:
        # Generate 6 digit OTP acak
        otp_code = str(random.randint(100000, 999999))
        
        # Simpan ke Redis dengan masa kedaluwarsa 5 menit (300 detik)
        cache_key = f"otp:{phone_number}"
        try:
            redis_client.setex(cache_key, 300, otp_code)
            return otp_code
        except Exception as e:
            logger.error(f"Gagal menyimpan OTP ke Redis: {e}")
            raise Exception("Gagal menyimpan OTP ke Redis. Pastikan server Redis berjalan.")
        
    @staticmethod
    def verify_otp(phone_number: str, otp_code: str) -> bool:
        cache_key = f"otp:{phone_number}"
        try:
            stored_otp = redis_client.get(cache_key)
            if stored_otp and stored_otp == otp_code:
                # Hapus OTP setelah berhasil diverifikasi agar tidak bisa dipakai 2 kali
                redis_client.delete(cache_key)
                return True
            return False
        except Exception as e:
            logger.error(f"Gagal memeriksa OTP dari Redis: {e}")
            raise Exception("Gagal memverifikasi OTP.")
