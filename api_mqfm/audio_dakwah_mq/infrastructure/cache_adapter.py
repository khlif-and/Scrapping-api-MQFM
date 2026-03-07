from typing import Optional
from audio_dakwah_mq.domain.port import AudioDakwahMqCachePort
from shared.cache import get_cache, set_cache, redis_client


class AudioDakwahMqCacheAdapter(AudioDakwahMqCachePort):
    CACHE_KEY = "audio_dakwah_mq"

    def get(self) -> Optional[dict]:
        return get_cache(self.CACHE_KEY)

    def set(self, data: dict) -> None:
        set_cache(self.CACHE_KEY, data, ex=7200)

    def invalidate(self) -> None:
        redis_client.delete(self.CACHE_KEY)
