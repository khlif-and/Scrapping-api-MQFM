import logging
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from program_and_adds.infrastructure.cache_adapter import ProgramAndAddsCacheAdapter
from program_and_adds.infrastructure.scraper_adapter import ProgramAndAddsScraperAdapter
from program_and_adds.application.use_case import GetProgramAndAddsUseCase

logger = logging.getLogger(__name__)
router = APIRouter()


class ProgramAndAddsItemResponse(BaseModel):
    title: str
    image_url: str


class ProgramAndAddsResponse(BaseModel):
    programs: List[ProgramAndAddsItemResponse]


@router.get("/program-and-adds", response_model=ProgramAndAddsResponse)
def get_program_and_adds():
    cache = ProgramAndAddsCacheAdapter()
    scraper = ProgramAndAddsScraperAdapter()
    use_case = GetProgramAndAddsUseCase(cache=cache, scraper=scraper)
    return use_case.execute()
