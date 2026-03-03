import logging
from fastapi import APIRouter
from services.program_and_adds_service import ProgramAndAddsService
from resources.program_and_adds_resource import ProgramAndAddsResource, ProgramAndAddsItemResource
from repositories.program_and_adds_repository import ProgramAndAddsRepository

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/program-and-adds", response_model=ProgramAndAddsResource)
def get_program_and_adds():
    cached_data = ProgramAndAddsRepository.get_cached_programs_and_adds()
    if cached_data:
        return cached_data

    programs = ProgramAndAddsService.scrape_program_and_adds()
    
    resource_data = ProgramAndAddsResource(
        programs=[ProgramAndAddsItemResource(title=p.title, image_url=p.image_url) for p in programs]
    )
    
    ProgramAndAddsRepository.set_cached_programs_and_adds(resource_data.model_dump())
    
    return resource_data
