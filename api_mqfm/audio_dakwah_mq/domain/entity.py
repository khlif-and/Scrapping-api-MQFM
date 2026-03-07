from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AudioDakwahMqTrackEntity:
    title: str
    mp3_url: str
    duration: Optional[str] = None


@dataclass
class AudioDakwahMqProgramEntity:
    title: str
    image_url: str
    page_url: str
    tracks: List[AudioDakwahMqTrackEntity] = field(default_factory=list)
