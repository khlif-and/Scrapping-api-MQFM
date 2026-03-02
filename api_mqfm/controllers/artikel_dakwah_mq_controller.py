import logging
from fastapi import APIRouter
from services.artikel_dakwah_mq_service import ArtikelDakwahMqService
from repositories.artikel_dakwah_mq_repository import ArtikelDakwahMqRepository
from resources.artikel_dakwah_mq_resource import ArtikelDakwahMqResource, ContentItemResource, ProgramItemResource

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/artikel-dakwah-mq", response_model=ArtikelDakwahMqResource)
def get_artikel_dakwah_mq():
    cached_data = ArtikelDakwahMqRepository.get_cached_artikel_dakwah_mq()
    if cached_data:
        return cached_data

    data = ArtikelDakwahMqService.scrape_data()
    
    resource_data = ArtikelDakwahMqResource(
        channel_name=data.channel_name,
        tagline=data.tagline,
        website=data.website,
        programs=[ProgramItemResource(program=p.program, schedule=p.schedule) for p in data.programs],
        contents=[ContentItemResource(title=c.title, link=c.link, image=c.image) for c in data.contents]
    )
    
    ArtikelDakwahMqRepository.set_cached_artikel_dakwah_mq(resource_data.model_dump())
    
    return resource_data
