import redis
import json
import logging

logger = logging.getLogger(__name__)

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


def get_cache(key: str):
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Failed to get cache for {key}: {e}")
    return None


def set_cache(key: str, data, ex: int = 3600):
    try:
        redis_client.setex(key, ex, json.dumps(data))
    except Exception as e:
        logger.warning(f"Failed to set cache for {key}: {e}")
