import logging
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from audio_dakwah_mq.infrastructure.cache_adapter import AudioDakwahMqCacheAdapter
from audio_dakwah_mq.infrastructure.scraper_adapter import AudioDakwahMqScraperAdapter
from audio_dakwah_mq.application.use_case import GetAudioDakwahMqUseCase

logger = logging.getLogger(__name__)
router = APIRouter()


class AudioTrackResponse(BaseModel):
    title: str
    mp3_url: str
    duration: Optional[str] = None


class AudioProgramResponse(BaseModel):
    title: str
    image_url: str
    page_url: str
    tracks: List[AudioTrackResponse] = []


class AudioDakwahMqResponse(BaseModel):
    programs: List[AudioProgramResponse]


@router.get("/audio-dakwah-mq", response_model=AudioDakwahMqResponse)
def get_audio_dakwah_mq():
    cache = AudioDakwahMqCacheAdapter()
    scraper = AudioDakwahMqScraperAdapter()
    use_case = GetAudioDakwahMqUseCase(cache=cache, scraper=scraper)
    return use_case.execute()
