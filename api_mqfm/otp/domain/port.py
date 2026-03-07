from abc import ABC, abstractmethod
from typing import Optional
from otp.domain.entity import OTPEntity


class OTPCachePort(ABC):
    @abstractmethod
    def save(self, entity: OTPEntity) -> bool:
        pass

    @abstractmethod
    def get(self, email: str) -> Optional[str]:
        pass

    @abstractmethod
    def delete(self, email: str) -> bool:
        pass


class OTPEmailPort(ABC):
    @abstractmethod
    def send_otp(self, email: str, otp_code: str) -> None:
        pass
