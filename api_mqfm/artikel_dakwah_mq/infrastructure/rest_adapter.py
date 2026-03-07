import logging
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from artikel_dakwah_mq.infrastructure.cache_adapter import ArtikelDakwahMqCacheAdapter
from artikel_dakwah_mq.infrastructure.scraper_adapter import ArtikelDakwahMqScraperAdapter
from artikel_dakwah_mq.application.use_case import GetArtikelDakwahMqUseCase

logger = logging.getLogger(__name__)
router = APIRouter()


class ProgramItemResponse(BaseModel):
    program: str
    schedule: str


class ContentItemResponse(BaseModel):
    title: str
    link: str
    image: Optional[str] = None


class ArtikelDakwahMqResponse(BaseModel):
    channel_name: str
    tagline: str
    website: str
    programs: List[ProgramItemResponse]
    contents: List[ContentItemResponse]


@router.get("/artikel-dakwah-mq", response_model=ArtikelDakwahMqResponse)
def get_artikel_dakwah_mq():
    cache = ArtikelDakwahMqCacheAdapter()
    scraper = ArtikelDakwahMqScraperAdapter()
    use_case = GetArtikelDakwahMqUseCase(cache=cache, scraper=scraper)
    return use_case.execute()
