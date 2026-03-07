from abc import ABC, abstractmethod
from typing import Optional
from artikel_dakwah_mq.domain.entity import ArtikelDakwahMqEntity


class ArtikelDakwahMqCachePort(ABC):
    @abstractmethod
    def get(self) -> Optional[dict]:
        pass

    @abstractmethod
    def set(self, data: dict) -> None:
        pass


class ArtikelDakwahMqScraperPort(ABC):
    @abstractmethod
    def scrape(self) -> ArtikelDakwahMqEntity:
        pass
