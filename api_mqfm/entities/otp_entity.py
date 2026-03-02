from dataclasses import dataclass
from typing import Optional

@dataclass
class OTPEntity:
    email: str
    otp_code: Optional[str] = None
    expires_in: int = 300
