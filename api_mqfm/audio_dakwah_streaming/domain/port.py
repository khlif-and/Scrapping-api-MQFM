from abc import ABC, abstractmethod
from typing import Optional
from audio_dakwah_streaming.domain.entity import AudioDakwahStreamingEntity


class AudioDakwahStreamingCachePort(ABC):
    @abstractmethod
    def get(self) -> Optional[dict]:
        pass

    @abstractmethod
    def set(self, data: dict) -> None:
        pass


class AudioDakwahStreamingScraperPort(ABC):
    @abstractmethod
    def scrape(self) -> AudioDakwahStreamingEntity:
        pass
