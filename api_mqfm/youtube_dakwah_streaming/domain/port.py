from abc import ABC, abstractmethod
from typing import Optional
from youtube_dakwah_streaming.domain.entity import YoutubeDakwahStreamingEntity


class YoutubeDakwahStreamingCachePort(ABC):
    @abstractmethod
    def get(self) -> Optional[dict]:
        pass

    @abstractmethod
    def set(self, data: dict) -> None:
        pass


class YoutubeDakwahStreamingScraperPort(ABC):
    @abstractmethod
    def scrape(self) -> YoutubeDakwahStreamingEntity:
        pass
