import logging
import requests
import os
from fastapi import HTTPException
from redis_client import get_cache, set_cache

logger = logging.getLogger(__name__)

class AudioDakwahStreamingRepository:
    @staticmethod
    def get_cached_streaming():
        try:
            return get_cache("audio_dakwah_streaming")
        except Exception as e:
            logger.error(f"Error reading streaming cache: {e}")
            return None

    @staticmethod
    def set_cached_streaming(data: dict):
        try:
            set_cache("audio_dakwah_streaming", data, ex=3600)
            return True
        except Exception as e:
            logger.error(f"Error writing streaming cache: {e}")
            return False

    @staticmethod
    def get_streaming_html(session: requests.Session, url: str):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
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

    @staticmethod
    def get_wp_ajax_schedule(session: requests.Session, wp_ajax_url: str, payload: dict):
        try:
            api_response = session.post(wp_ajax_url, data=payload, timeout=5)
            if api_response.status_code == 200:
                try:
                    return api_response.json()
                except Exception as e:
                    logger.warning(f"Gagal parse REST API WP AJAX: {e}")
            return None
        except Exception as e:
            logger.warning(f"Request REST API WP AJAX error: {e}")
            return None
