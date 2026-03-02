from redis_client import redis_client
from entities.otp_entity import OTPEntity
import logging

logger = logging.getLogger(__name__)

class OTPRepository:
    @staticmethod
    def save_otp(entity: OTPEntity) -> bool:
        cache_key = f"otp:{entity.email}"
        try:
            redis_client.setex(cache_key, entity.expires_in, entity.otp_code)
            return True
        except Exception as e:
            logger.error(f"Generate OTP Repo Error: {e}")
            return False

    @staticmethod
    def get_otp(email: str) -> str:
        cache_key = f"otp:{email}"
        try:
            return redis_client.get(cache_key)
        except Exception as e:
            logger.error(f"Get OTP Repo Error: {e}")
            return None

    @staticmethod
    def delete_otp(email: str) -> bool:
        cache_key = f"otp:{email}"
        try:
            redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Delete OTP Repo Error: {e}")
            return False
