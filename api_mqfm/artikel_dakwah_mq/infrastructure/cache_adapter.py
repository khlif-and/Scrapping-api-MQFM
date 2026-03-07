from typing import Optional
from artikel_dakwah_mq.domain.port import ArtikelDakwahMqCachePort
from shared.cache import get_cache, set_cache, redis_client


class ArtikelDakwahMqCacheAdapter(ArtikelDakwahMqCachePort):
    CACHE_KEY = "artikel_dakwah_mq_data"

    def get(self) -> Optional[dict]:
        return get_cache(self.CACHE_KEY)

    def set(self, data: dict) -> None:
        set_cache(self.CACHE_KEY, data, ex=7200)

    def invalidate(self) -> None:
        redis_client.delete(self.CACHE_KEY)
