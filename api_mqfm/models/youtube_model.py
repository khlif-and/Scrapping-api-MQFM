from pydantic import BaseModel
from typing import Optional

class YoutubeStreamInfo(BaseModel):
    youtube_url: Optional[str] = None
    title: Optional[str] = None
