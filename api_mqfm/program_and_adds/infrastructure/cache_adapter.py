from typing import Optional
from program_and_adds.domain.port import ProgramAndAddsCachePort
from shared.cache import get_cache, set_cache, redis_client


class ProgramAndAddsCacheAdapter(ProgramAndAddsCachePort):
    CACHE_KEY = "program_and_adds"

    def get(self) -> Optional[dict]:
        return get_cache(self.CACHE_KEY)

    def set(self, data: dict) -> None:
        set_cache(self.CACHE_KEY, data, ex=7200)

    def invalidate(self) -> None:
        redis_client.delete(self.CACHE_KEY)
