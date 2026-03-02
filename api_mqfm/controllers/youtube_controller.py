import logging
import requests
from fastapi import APIRouter, HTTPException
from services.youtube_service import YoutubeService
from models.youtube_model import YoutubeStreamInfo
from redis_client import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/youtube-streaming", response_model=YoutubeStreamInfo)
def get_youtube_streaming():
    try:
        cache_key = "youtube_streaming"
        cached_data = get_cache(cache_key)
        if cached_data:
            return cached_data

        data = YoutubeService.scrape_youtube_stream()
        
        # Cek apakah youtube livestream sedang tidak aktif
        if not data.youtube_url:
            logger.info("Siaran Live Streaming YouTube saat ini sedang tidak aktif atau sudah selesai.")
            raise HTTPException(status_code=404, detail="Live Streaming YouTube saat ini tidak tersedia atau sudah selesai.")
            
        set_cache(cache_key, data.model_dump(), ex=3600)
        return data
    except HTTPException as e:
        # Biarkan pesan 404 "Tidak aktif" keluar dengan benar
        raise e
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Error koneksi internet saat mengambil Youtube Stream: {e}")
        raise HTTPException(status_code=503, detail="Gagal menghubungi server. Pastikan internet Anda aktif.")
    except requests.exceptions.Timeout as e:
        logger.error(f"Request timeout saat mengambil Youtube Stream: {e}")
        raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout).")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error saat mengambil Youtube Stream: {e}")
        raise HTTPException(status_code=502, detail="Server bermasalah atau menolak permintaan (HTTP Error).")
    except requests.exceptions.RequestException as e:
        logger.error(f"Gangguan jaringan tidak terduga: {e}")
        raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat memuat URL Youtube.")
    except Exception as e:
        logger.error(f"Internal server error pada Youtube scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal pada pencarian plugin YouTube di API.")
