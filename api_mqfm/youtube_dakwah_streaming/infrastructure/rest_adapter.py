import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from youtube_dakwah_streaming.infrastructure.cache_adapter import YoutubeDakwahStreamingCacheAdapter
from youtube_dakwah_streaming.infrastructure.scraper_adapter import YoutubeDakwahStreamingScraperAdapter
from youtube_dakwah_streaming.application.use_case import GetYoutubeDakwahStreamingUseCase

logger = logging.getLogger(__name__)
router = APIRouter()


class YoutubeDakwahStreamingResponse(BaseModel):
    youtube_url: Optional[str] = None
    title: Optional[str] = None


@router.get("/youtube-dakwah-streaming", response_model=YoutubeDakwahStreamingResponse)
def get_youtube_dakwah_streaming():
    cache = YoutubeDakwahStreamingCacheAdapter()
    scraper = YoutubeDakwahStreamingScraperAdapter()
    use_case = GetYoutubeDakwahStreamingUseCase(cache=cache, scraper=scraper)
    data = use_case.execute()

    if not data.get("available", True) or not data.get("youtube_url"):
        logger.info("Siaran Live Streaming YouTube saat ini sedang tidak aktif atau sudah selesai.")
        raise HTTPException(status_code=404, detail="Live Streaming YouTube saat ini tidak tersedia atau sudah selesai.")

    return data
