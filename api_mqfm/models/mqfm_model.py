from pydantic import BaseModel
from typing import List, Optional

class ContentItem(BaseModel):
    title: str
    link: str
    image: Optional[str] = None

class ProgramItem(BaseModel):
    program: str
    schedule: str

class MqfmData(BaseModel):
    channel_name: str
    tagline: str
    website: str
    programs: List[ProgramItem]
    contents: List[ContentItem]
