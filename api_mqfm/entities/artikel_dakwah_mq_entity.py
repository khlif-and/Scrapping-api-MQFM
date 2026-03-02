from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ProgramEntity:
    program: str
    schedule: str

@dataclass
class ContentEntity:
    title: str
    link: str
    image: Optional[str] = None

@dataclass
class ArtikelDakwahMqEntity:
    channel_name: str
    tagline: str
    website: str
    programs: List[ProgramEntity] = field(default_factory=list)
    contents: List[ContentEntity] = field(default_factory=list)
