from pydantic import BaseModel
from typing import List, Optional

class AudioTrackModel(BaseModel):
    title: str
    mp3_url: str
    duration: Optional[str] = None

class AudioProgramModel(BaseModel):
    title: str
    image_url: str
    page_url: str
    tracks: List[AudioTrackModel] = []

class AudioOnDemandResponse(BaseModel):
    programs: List[AudioProgramModel]
