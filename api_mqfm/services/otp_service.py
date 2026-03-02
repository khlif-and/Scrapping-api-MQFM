import random
from entities.otp_entity import OTPEntity
from repositories.otp_repository import OTPRepository

class OTPService:
    @staticmethod
    def generate_otp(email: str) -> OTPEntity:
        otp_code = str(random.randint(100000, 999999))
        entity = OTPEntity(email=email, otp_code=otp_code)
        
        saved = OTPRepository.save_otp(entity)
        if not saved:
            raise Exception("Gagal menyimpan OTP ke Repository.")
            
        return entity

    @staticmethod
    def verify_otp(email: str, otp_code: str) -> bool:
        stored_otp = OTPRepository.get_otp(email)
        
        if stored_otp and stored_otp == otp_code:
            OTPRepository.delete_otp(email)
            return True
            
        return False
