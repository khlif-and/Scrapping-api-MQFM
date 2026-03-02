from redis_client import get_cache, set_cache
import logging
import requests
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ArtikelDakwahMqRepository:
    @staticmethod
    def get_cached_artikel_dakwah_mq():
        try:
            return get_cache("artikel_dakwah_mq_data")
        except Exception as e:
            logger.error(f"Error reading artikel_dakwah_mq cache: {e}")
            return None

    @staticmethod
    def set_cached_artikel_dakwah_mq(data: dict):
        try:
            set_cache("artikel_dakwah_mq_data", data, ex=3600)
            return True
        except Exception as e:
            logger.error(f"Error writing artikel_dakwah_mq cache: {e}")
            return False

    @staticmethod
    def get_mqfm_html(session: requests.Session, url: str):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
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
