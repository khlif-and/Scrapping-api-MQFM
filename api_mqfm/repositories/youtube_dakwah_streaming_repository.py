import logging
import requests
import yt_dlp
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
    def create_session(headers: dict) -> requests.Session:
        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']
        return session

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
    def validate_youtube_live_with_ytdlp(youtube_url: str) -> dict | None:
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)

                if info:
                    is_live = info.get('is_live', False)
                    title = info.get('title', '')
                    webpage_url = info.get('webpage_url', youtube_url)

                    logger.info(f"yt-dlp result - is_live: {is_live}, title: {title}")

                    return {
                        'is_live': is_live,
                        'title': title,
                        'url': webpage_url
                    }

            return None
        except Exception as e:
            logger.warning(f"yt-dlp gagal validasi live status YouTube: {e}")
            return None
