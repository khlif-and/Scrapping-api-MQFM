import logging
import requests
from fastapi import APIRouter, HTTPException
from services.streaming_service import StreamingService
from models.streaming_model import StreamingInfo

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/streaming", response_model=StreamingInfo)
def get_streaming_data():
    try:
        data = StreamingService.scrape_streaming_data()
        return data
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error koneksi internet saat memuat jadwal: {e}")
        raise HTTPException(status_code=503, detail="Gagal menghubungi server MQFM. Pastikan internet Anda aktif atau server tidak down.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout server MQFM saat memuat jadwal: {e}")
        raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout) saat menghubungi server MQFM.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error server MQFM saat memuat jadwal: {e}")
        raise HTTPException(status_code=502, detail="Server MQFM bermasalah atau menolak permintaan (HTTP Error).")
    except requests.exceptions.RequestException as e:
        logger.error(f"Gangguan jaringan tidak terduga: {e}")
        raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat mengambil data jadwal dari MQFM.")
    except Exception as e:
        logger.error(f"Internal server error pada saat scraping jadwal: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal sistem API pada saat web scraping.")
