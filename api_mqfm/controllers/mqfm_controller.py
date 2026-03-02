import logging
import requests
from fastapi import APIRouter, HTTPException
from services.mqfm_service import MqfmService
from models.mqfm_model import MqfmData
from redis_client import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/mqfm", response_model=MqfmData)
def get_mqfm_data():
    try:
        cache_key = "mqfm_data"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        data = MqfmService.scrape_data()
        set_cache(cache_key, data.model_dump(), ex=3600)
        return data
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error koneksi internet atau server MQFM down: {e}")
        raise HTTPException(status_code=503, detail="Gagal menghubungi server MQFM. Pastikan internet Anda aktif atau server tidak down.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout ke server MQFM: {e}")
        raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout) saat mencoba menghubungi server MQFM.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"Server MQFM merespon dengan error HTTP: {e}")
        raise HTTPException(status_code=502, detail="Server MQFM bermasalah atau menolak permintaan (HTTP Error).")
    except requests.exceptions.RequestException as e:
        logger.error(f"Gangguan jaringan tidak terduga: {e}")
        raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat mengambil data dari MQFM.")
    except Exception as e:
        logger.error(f"Internal server error pada saat scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal sistem API pada saat web scraping.")
