from redis_client import get_cache, set_cache
import logging
import requests
from fastapi import HTTPException
from services.audio_dakwah_mq_service import AudioDakwahMqService

logger = logging.getLogger(__name__)

class AudioDakwahMqRepository:
    @staticmethod
    def get_cached_audio_dakwah_mq():
        try:
            return get_cache("audio_dakwah_mq")
        except Exception as e:
            logger.error(f"Error reading audio cache: {e}")
            return None

    @staticmethod
    def set_cached_audio_dakwah_mq(data: dict):
        try:
            set_cache("audio_dakwah_mq", data, ex=3600)
            return True
        except Exception as e:
            logger.error(f"Error writing audio cache: {e}")
            return False

    @staticmethod
    def get_sub_page_html(session, page_url):
        try:
            sub_resp = session.get(page_url, timeout=5)
            if sub_resp.status_code == 200:
                return sub_resp.text
        except Exception as e:
            logger.warning(f"Gagal mengambil track untuk {page_url}: {e}")
        return None

    @staticmethod
    def get_wp_media_json(session, wp_api_url, media_headers):
        try:
            api_resp = session.get(wp_api_url, headers=media_headers, timeout=10)
            if api_resp.status_code == 200:
                try:
                    return api_resp.json()
                except Exception as e:
                    logger.warning(f"Gagal parse REST API WP: {e}")
            else:
                logger.warning(f"REST API WP menolak request: {api_resp.status_code}")
        except Exception as e:
            logger.warning(f"Request REST API WP error: {e}")
        return None

    @staticmethod
    def fetch_and_cache_audio_dakwah_mq():
        try:
            programs = AudioDakwahMqService.scrape_audio_dakwah_mq()
            return programs
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
