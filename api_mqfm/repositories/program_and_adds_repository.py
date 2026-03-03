import logging
import requests
from fastapi import HTTPException
from redis_client import get_cache, set_cache

logger = logging.getLogger(__name__)

class ProgramAndAddsRepository:
    @staticmethod
    def get_cached_programs_and_adds():
        try:
            return get_cache("program_and_adds")
        except Exception as e:
            logger.error(f"Error reading program_and_adds cache: {e}")
            return None

    @staticmethod
    def set_cached_programs_and_adds(data: dict):
        try:
            set_cache("program_and_adds", data, ex=3600)
            return True
        except Exception as e:
            logger.error(f"Error writing program_and_adds cache: {e}")
            return False

    @staticmethod
    def get_mqfm_html(session: requests.Session, url: str):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
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
