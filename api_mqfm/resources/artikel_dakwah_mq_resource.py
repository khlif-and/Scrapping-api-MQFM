from pydantic import BaseModel
from typing import List, Optional

class ProgramItemResource(BaseModel):
    program: str
    schedule: str

class ContentItemResource(BaseModel):
    title: str
    link: str
    image: Optional[str] = None

class ArtikelDakwahMqResource(BaseModel):
    channel_name: str
    tagline: str
    website: str
    programs: List[ProgramItemResource]
    contents: List[ContentItemResource]
