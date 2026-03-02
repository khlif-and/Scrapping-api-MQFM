import logging
import requests
from fastapi import APIRouter, HTTPException
from services.audio_service import AudioService
from models.audio_model import AudioOnDemandResponse
from redis_client import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/audio-on-demand", response_model=AudioOnDemandResponse)
def get_audio_on_demand():
    try:
        cache_key = "audio_on_demand"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        programs = AudioService.scrape_audio_on_demand()
        response_data = AudioOnDemandResponse(programs=programs)
        set_cache(cache_key, response_data.model_dump(), ex=3600)
        return response_data
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error koneksi internet saat mengambil Audio On Demand: {e}")
        raise HTTPException(status_code=503, detail="Gagal menghubungi server MQFM. Pastikan internet Anda aktif.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout saat mengambil Audio On Demand: {e}")
        raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout).")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error saat mengambil Audio On Demand: {e}")
        raise HTTPException(status_code=502, detail="Server bermasalah atau menolak permintaan (HTTP Error).")
    except requests.exceptions.RequestException as e:
        logger.error(f"Gangguan jaringan tidak terduga: {e}")
        raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat memuat data Audio On Demand.")
    except Exception as e:
        logger.error(f"Internal server error pada Audio scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal ketika melakukan web scraping Audio On Demand.")
