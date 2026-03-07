import os
import logging
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fastapi import HTTPException
from audio_dakwah_streaming.domain.entity import AudioDakwahStreamingEntity
from audio_dakwah_streaming.domain.port import AudioDakwahStreamingScraperPort

load_dotenv()
logger = logging.getLogger(__name__)


class AudioDakwahStreamingScraperAdapter(AudioDakwahStreamingScraperPort):
    def scrape(self) -> AudioDakwahStreamingEntity:
        url = os.getenv('AUDIO_DAKWAH_STREAMING_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }

        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']

        html_content = self._fetch_html(session, url)

        current_program = None
        schedule = None
        audio_url = None
        up_next_program = None
        up_next_schedule = None

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')

            audio_tag = soup.find('audio')
            if audio_tag:
                source_tag = audio_tag.find('source')
                if source_tag and source_tag.get('src'):
                    audio_url = source_tag.get('src')
                elif audio_tag.get('src'):
                    audio_url = audio_tag.get('src')

            iframe_tag = soup.find('iframe')
            if not audio_url and iframe_tag and iframe_tag.get('src'):
                if 'radio' in iframe_tag.get('src').lower() or 'stream' in iframe_tag.get('src').lower() or 'zeno' in iframe_tag.get('src').lower():
                    audio_url = iframe_tag.get('src')

            elements_with_text = soup.find_all(['h2', 'h3', 'h4', 'span', 'div', 'p'])
            for el in elements_with_text:
                text = el.get_text(strip=True).upper()
                if 'LIVE' in text or 'NOW PLAYING' in text or 'SEDANG SIARAN' in text:
                    for sibling in el.find_next_siblings(['h2', 'h3', 'h4', 'span', 'p', 'div']):
                        sibling_text = sibling.get_text(strip=True)
                        if sibling_text and not sibling_text.isspace() and len(sibling_text) > 3:
                            current_program = sibling_text
                            break
                    if current_program:
                        break

            if not current_program:
                headings = soup.find_all(['h2', 'h3', 'h4'])
                for h in headings:
                    text = h.get_text(strip=True)
                    if text and len(text) > 5 and 'STREAMING' not in text.upper() and 'MQFM' not in text.upper() and 'AUDIO' not in text.upper():
                        current_program = text
                        break

            wp_ajax_url = os.getenv('WP_AJAX_URL')
            payload = {
                'action': 'show_time_curd',
                'crud-action': 'read',
                'read-type': 'current'
            }
            schedule_data = self._fetch_wp_ajax(session, wp_ajax_url, payload)

            if isinstance(schedule_data, dict):
                current_show = schedule_data.get('current_show')
                if isinstance(current_show, dict):
                    current_program = current_show.get('show_name', current_program)
                    start = current_show.get('start_time', '')[:5]
                    end = current_show.get('end_time', '')[:5]
                    if start and end:
                        schedule = f"{start} - {end}"

                upcoming_show = schedule_data.get('upcoming_show')
                if isinstance(upcoming_show, dict):
                    up_next_program = upcoming_show.get('show_name')
                    start_next = upcoming_show.get('start_time', '')[:5]
                    end_next = upcoming_show.get('end_time', '')[:5]
                    if start_next and end_next:
                        up_next_schedule = f"{start_next} - {end_next}"

            if not current_program or current_program == "•Live Streaming" or current_program == "Live StreamingAudio on Demand" or "Live Streaming" in current_program:
                current_program = "Live On Air 102.7 MQFM Bandung"

            if not schedule:
                schedule = "On Air 24 Jam"

        return AudioDakwahStreamingEntity(
            current_program=current_program,
            schedule=schedule,
            up_next_program=up_next_program,
            up_next_schedule=up_next_schedule,
            audio_url=audio_url
        )

    def _fetch_html(self, session: requests.Session, url: str) -> str:
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

    def _fetch_wp_ajax(self, session: requests.Session, wp_ajax_url: str, payload: dict):
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
