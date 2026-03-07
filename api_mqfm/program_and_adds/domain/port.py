from abc import ABC, abstractmethod
from typing import Optional, List
from program_and_adds.domain.entity import ProgramAndAddsEntity


class ProgramAndAddsCachePort(ABC):
    @abstractmethod
    def get(self) -> Optional[dict]:
        pass

    @abstractmethod
    def set(self, data: dict) -> None:
        pass


class ProgramAndAddsScraperPort(ABC):
    @abstractmethod
    def scrape(self) -> List[ProgramAndAddsEntity]:
        pass
