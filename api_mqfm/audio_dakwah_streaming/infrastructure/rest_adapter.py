import logging
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from audio_dakwah_streaming.infrastructure.cache_adapter import AudioDakwahStreamingCacheAdapter
from audio_dakwah_streaming.infrastructure.scraper_adapter import AudioDakwahStreamingScraperAdapter
from audio_dakwah_streaming.application.use_case import GetAudioDakwahStreamingUseCase

logger = logging.getLogger(__name__)
router = APIRouter()


class AudioDakwahStreamingResponse(BaseModel):
    current_program: Optional[str] = None
    schedule: Optional[str] = None
    up_next_program: Optional[str] = None
    up_next_schedule: Optional[str] = None
    audio_url: Optional[str] = None


@router.get("/audio-dakwah-streaming", response_model=AudioDakwahStreamingResponse)
def get_audio_dakwah_streaming():
    cache = AudioDakwahStreamingCacheAdapter()
    scraper = AudioDakwahStreamingScraperAdapter()
    use_case = GetAudioDakwahStreamingUseCase(cache=cache, scraper=scraper)
    return use_case.execute()
