import os
import logging
import requests
import yt_dlp
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fastapi import HTTPException
from youtube_dakwah_streaming.domain.entity import YoutubeDakwahStreamingEntity
from youtube_dakwah_streaming.domain.port import YoutubeDakwahStreamingScraperPort

load_dotenv()
logger = logging.getLogger(__name__)


class YoutubeDakwahStreamingScraperAdapter(YoutubeDakwahStreamingScraperPort):
    def scrape(self) -> YoutubeDakwahStreamingEntity:
        url = os.getenv('AUDIO_DAKWAH_STREAMING_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }

        session = self._create_session(headers)
        html_content = self._fetch_html(session, url)

        youtube_url = None
        title = None

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')

            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src')
                if src and ('youtube.com' in src or 'youtu.be' in src):
                    if '/embed/live_stream?channel=' in src:
                        channel_id = src.split('channel=')[1].split('&')[0]
                        base_url = os.getenv('YOUTUBE_CHANNEL_BASE_URL')
                        youtube_url = f"{base_url}{channel_id}/live"
                    elif '/embed/' in src:
                        video_id = src.split('/embed/')[1].split('?')[0]
                        base_url = os.getenv('YOUTUBE_WATCH_BASE_URL')
                        youtube_url = f"{base_url}{video_id}"
                    else:
                        youtube_url = src
                    title = iframe.get('title')
                    break

            if not youtube_url:
                links = soup.find_all('a')
                for a in links:
                    href = a.get('href')
                    if href and ('youtube.com/watch' in href or 'youtube.com/live' in href or 'youtu.be' in href):
                        parent_text = a.find_parent().get_text(strip=True).upper()
                        if 'LIVE' in parent_text or 'STREAMING' in parent_text:
                            youtube_url = href
                            title = a.get_text(strip=True) or (a.get('title'))
                            if title and len(title) > 3:
                                break

            if not title and youtube_url:
                title = "MQFM Live YouTube Stream"

            if youtube_url:
                live_info = self._validate_youtube_live(youtube_url)
                if live_info and live_info.get('is_live'):
                    title = live_info.get('title', title)
                    youtube_url = live_info.get('url', youtube_url)
                else:
                    logger.info(f"YouTube tidak sedang live berdasarkan yt-dlp: {youtube_url}")
                    youtube_url = None
                    title = None

        return YoutubeDakwahStreamingEntity(youtube_url=youtube_url, title=title)

    def _create_session(self, headers: dict) -> requests.Session:
        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']
        return session

    def _fetch_html(self, session: requests.Session, url: str) -> str:
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

    def _validate_youtube_live(self, youtube_url: str) -> dict:
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
                    return {
                        'is_live': info.get('is_live', False),
                        'title': info.get('title', ''),
                        'url': info.get('webpage_url', youtube_url)
                    }
            return None
        except Exception as e:
            logger.warning(f"yt-dlp gagal validasi live status YouTube: {e}")
            return None
