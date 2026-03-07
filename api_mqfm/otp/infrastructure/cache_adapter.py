import logging
from typing import Optional
from shared.cache import redis_client
from otp.domain.entity import OTPEntity
from otp.domain.port import OTPCachePort

logger = logging.getLogger(__name__)


class OTPCacheAdapter(OTPCachePort):
    def save(self, entity: OTPEntity) -> bool:
        cache_key = f"otp:{entity.email}"
        try:
            redis_client.setex(cache_key, entity.expires_in, entity.otp_code)
            return True
        except Exception as e:
            logger.error(f"Generate OTP Repo Error: {e}")
            return False

    def get(self, email: str) -> Optional[str]:
        cache_key = f"otp:{email}"
        try:
            return redis_client.get(cache_key)
        except Exception as e:
            logger.error(f"Get OTP Repo Error: {e}")
            return None

    def delete(self, email: str) -> bool:
        cache_key = f"otp:{email}"
        try:
            redis_client.delete(cache_key)
            return True
        except Exception as e:
            logger.error(f"Delete OTP Repo Error: {e}")
            return False
