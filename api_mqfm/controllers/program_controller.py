import logging
import requests
from fastapi import APIRouter, HTTPException
from services.program_service import ProgramService
from resources.program_resource import ProgramResource, ProgramItemResource
from repositories.program_repository import ProgramRepository

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/programs", response_model=ProgramResource)
def get_programs_on_air():
    try:
        cached_data = ProgramRepository.get_cached_programs()
        if cached_data:
            return cached_data

        programs = ProgramService.scrape_program_on_air()
        
        resource_data = ProgramResource(
            programs=[ProgramItemResource(title=p.title, image_url=p.image_url) for p in programs]
        )
        
        ProgramRepository.set_cached_programs(resource_data.model_dump())
        
        return resource_data
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error koneksi internet saat mengambil Program On Air: {e}")
        raise HTTPException(status_code=503, detail="Gagal menghubungi server MQFM. Pastikan internet Anda aktif.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout saat mengambil Program On Air: {e}")
        raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout).")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error saat mengambil Program On Air: {e}")
        raise HTTPException(status_code=502, detail="Server MQFM bermasalah atau menolak permintaan (HTTP Error).")
    except requests.exceptions.RequestException as e:
        logger.error(f"Gangguan jaringan tidak terduga: {e}")
        raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat memuat Program On Air.")
    except Exception as e:
        logger.error(f"Internal server error pada Program On Air scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal pada saat web scraping Program On Air.")
