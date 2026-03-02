import logging
from fastapi import APIRouter
from services.audio_dakwah_streaming_service import AudioDakwahStreamingService
from repositories.audio_dakwah_streaming_repository import AudioDakwahStreamingRepository
from resources.audio_dakwah_streaming_resource import AudioDakwahStreamingResource

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/audio-dakwah-streaming", response_model=AudioDakwahStreamingResource)
def get_audio_dakwah_streaming():
    cached_data = AudioDakwahStreamingRepository.get_cached_streaming()
    if cached_data:
        return cached_data

    entity_data = AudioDakwahStreamingService.scrape_audio_dakwah_streaming()
    
    resource_data = AudioDakwahStreamingResource(
        current_program=entity_data.current_program,
        schedule=entity_data.schedule,
        up_next_program=entity_data.up_next_program,
        up_next_schedule=entity_data.up_next_schedule,
        audio_url=entity_data.audio_url
    )
    
    AudioDakwahStreamingRepository.set_cached_streaming(resource_data.model_dump())
    
    return resource_data
