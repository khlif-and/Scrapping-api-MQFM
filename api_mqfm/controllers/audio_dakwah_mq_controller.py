import logging
from fastapi import APIRouter
from repositories.audio_dakwah_mq_repository import AudioDakwahMqRepository
from resources.audio_dakwah_mq_resource import AudioDakwahMqResource, AudioDakwahMqProgramResource, AudioDakwahMqTrackResource

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/audio-dakwah-mq", response_model=AudioDakwahMqResource)
def get_audio_dakwah_mq():
    cached_data = AudioDakwahMqRepository.get_cached_audio_dakwah_mq()
    if cached_data:
        return cached_data

    programs = AudioDakwahMqRepository.fetch_and_cache_audio_dakwah_mq()
    
    resource_data = AudioDakwahMqResource(
        programs=[
            AudioDakwahMqProgramResource(
                title=p.title,
                image_url=p.image_url,
                page_url=p.page_url,
                tracks=[
                    AudioDakwahMqTrackResource(title=t.title, mp3_url=t.mp3_url, duration=t.duration)
                    for t in p.tracks
                ]
            ) for p in programs
        ]
    )
    
    AudioDakwahMqRepository.set_cached_audio_dakwah_mq(resource_data.model_dump())
    return resource_data
