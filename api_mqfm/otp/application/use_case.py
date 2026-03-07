import random
from otp.domain.entity import OTPEntity
from otp.domain.port import OTPCachePort, OTPEmailPort


class GenerateOTPUseCase:
    def __init__(self, cache: OTPCachePort, email_sender: OTPEmailPort):
        self._cache = cache
        self._email_sender = email_sender

    def execute(self, email: str) -> dict:
        otp_code = str(random.randint(100000, 999999))
        entity = OTPEntity(email=email, otp_code=otp_code)

        saved = self._cache.save(entity)
        if not saved:
            return {"success": False, "message": "Gagal menyimpan OTP ke Repository."}

        self._email_sender.send_otp(email, otp_code)

        return {
            "success": True,
            "message": f"Kode OTP berhasil digenerate dan dikirim ke {email}.",
        }


class VerifyOTPUseCase:
    def __init__(self, cache: OTPCachePort):
        self._cache = cache

    def execute(self, email: str, otp_code: str) -> dict:
        stored_otp = self._cache.get(email)

        if stored_otp and stored_otp == otp_code:
            self._cache.delete(email)
            return {"success": True, "message": "OTP Valid! Verifikasi berhasil."}

        return {"success": False, "message": "OTP tidak valid atau sudah kedaluwarsa."}
