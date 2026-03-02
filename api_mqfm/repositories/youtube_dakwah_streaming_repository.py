import logging
import requests
from fastapi import HTTPException
from redis_client import get_cache, set_cache

logger = logging.getLogger(__name__)

class YoutubeDakwahStreamingRepository:
    @staticmethod
    def get_cached_youtube_streaming():
        try:
            return get_cache("youtube_dakwah_streaming")
        except Exception as e:
            logger.error(f"Error reading youtube streaming cache: {e}")
            return None

    @staticmethod
    def set_cached_youtube_streaming(data: dict):
        try:
            set_cache("youtube_dakwah_streaming", data, ex=3600)
            return True
        except Exception as e:
            logger.error(f"Error writing youtube streaming cache: {e}")
            return False

    @staticmethod
    def get_youtube_html(session: requests.Session, url: str):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
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
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal pada pencarian modul YouTube di API.")

    @staticmethod
    def validate_youtube_live_status(session: requests.Session, youtube_url: str):
        try:
            yt_resp = session.get(youtube_url, timeout=10)
            if yt_resp.status_code == 200:
                return yt_resp.text
            return None
        except Exception as e:
            logger.warning(f"Error validasi live status YouTube: {e}")
            return None
