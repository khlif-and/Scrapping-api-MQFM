from pydantic import BaseModel
from typing import Optional

class AudioDakwahStreamingResource(BaseModel):
    current_program: Optional[str] = None
    schedule: Optional[str] = None
    up_next_program: Optional[str] = None
    up_next_schedule: Optional[str] = None
    audio_url: Optional[str] = None
