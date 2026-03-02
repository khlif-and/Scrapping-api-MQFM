import logging
from fastapi import APIRouter, HTTPException
from services.youtube_dakwah_streaming_service import YoutubeDakwahStreamingService
from repositories.youtube_dakwah_streaming_repository import YoutubeDakwahStreamingRepository
from resources.youtube_dakwah_streaming_resource import YoutubeDakwahStreamingResource

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/youtube-dakwah-streaming", response_model=YoutubeDakwahStreamingResource)
def get_youtube_dakwah_streaming():
    cached_data = YoutubeDakwahStreamingRepository.get_cached_youtube_streaming()
    if cached_data:
        return cached_data

    entity_data = YoutubeDakwahStreamingService.scrape_youtube_dakwah_streaming()
    
    if not entity_data.youtube_url:
        logger.info("Siaran Live Streaming YouTube saat ini sedang tidak aktif atau sudah selesai.")
        raise HTTPException(status_code=404, detail="Live Streaming YouTube saat ini tidak tersedia atau sudah selesai.")
        
    resource_data = YoutubeDakwahStreamingResource(
        youtube_url=entity_data.youtube_url,
        title=entity_data.title
    )
    
    YoutubeDakwahStreamingRepository.set_cached_youtube_streaming(resource_data.model_dump())
    
    return resource_data
