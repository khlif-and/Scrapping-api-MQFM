from dataclasses import dataclass
from typing import Optional


@dataclass
class YoutubeDakwahStreamingEntity:
    youtube_url: Optional[str] = None
    title: Optional[str] = None
