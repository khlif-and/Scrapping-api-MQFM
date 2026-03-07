from abc import ABC, abstractmethod
from typing import Optional, List
from audio_dakwah_mq.domain.entity import AudioDakwahMqProgramEntity


class AudioDakwahMqCachePort(ABC):
    @abstractmethod
    def get(self) -> Optional[dict]:
        pass

    @abstractmethod
    def set(self, data: dict) -> None:
        pass


class AudioDakwahMqScraperPort(ABC):
    @abstractmethod
    def scrape(self) -> List[AudioDakwahMqProgramEntity]:
        pass
