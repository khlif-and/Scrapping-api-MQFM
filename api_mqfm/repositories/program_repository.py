from redis_client import get_cache, set_cache
import logging

logger = logging.getLogger(__name__)

class ProgramRepository:
    @staticmethod
    def get_cached_programs():
        try:
            return get_cache("programs_on_air")
        except Exception as e:
            logger.error(f"Error reading cache: {e}")
            return None

    @staticmethod
    def set_cached_programs(data: dict):
        try:
            set_cache("programs_on_air", data, ex=3600)
            return True
        except Exception as e:
            logger.error(f"Error writing cache: {e}")
            return False
