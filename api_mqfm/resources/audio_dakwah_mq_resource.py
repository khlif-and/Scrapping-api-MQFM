from pydantic import BaseModel
from typing import List, Optional

class AudioDakwahMqTrackResource(BaseModel):
    title: str
    mp3_url: str
    duration: Optional[str] = None

class AudioDakwahMqProgramResource(BaseModel):
    title: str
    image_url: str
    page_url: str
    tracks: List[AudioDakwahMqTrackResource] = []

class AudioDakwahMqResource(BaseModel):
    programs: List[AudioDakwahMqProgramResource]
