from typing import Optional
from audio_dakwah_streaming.domain.port import AudioDakwahStreamingCachePort
from shared.cache import get_cache, set_cache, redis_client


class AudioDakwahStreamingCacheAdapter(AudioDakwahStreamingCachePort):
    CACHE_KEY = "audio_dakwah_streaming"

    def get(self) -> Optional[dict]:
        return get_cache(self.CACHE_KEY)

    def set(self, data: dict) -> None:
        set_cache(self.CACHE_KEY, data, ex=600)

    def invalidate(self) -> None:
        redis_client.delete(self.CACHE_KEY)
