import os
import re
import json
import logging
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List
from fastapi import HTTPException
from audio_dakwah_mq.domain.entity import AudioDakwahMqProgramEntity, AudioDakwahMqTrackEntity
from audio_dakwah_mq.domain.port import AudioDakwahMqScraperPort

load_dotenv()
logger = logging.getLogger(__name__)


class AudioDakwahMqScraperAdapter(AudioDakwahMqScraperPort):
    def scrape(self) -> List[AudioDakwahMqProgramEntity]:
        url = os.getenv('AUDIO_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }

        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
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

        soup = BeautifulSoup(response.text, 'html.parser')
        programs = []
        columns = soup.find_all(class_='elementor-column')
        seen_urls = set()

        for col in columns:
            img_el = col.find('img')
            btn_link = col.find('a', class_='elementor-button-link')

            if img_el and btn_link:
                page_url = btn_link.get('href')

                if not page_url or 'audio-on-demand' in page_url and page_url.strip('/').endswith('audio-on-demand'):
                    continue

                if page_url in seen_urls:
                    continue
                seen_urls.add(page_url)

                img_url = img_el.get('src')
                title = img_el.get('alt', '').strip()
                if not title:
                    title = page_url.strip('/').split('/')[-1].replace('-', ' ').title()

                tracks = self._fetch_tracks(session, page_url, headers)

                programs.append(AudioDakwahMqProgramEntity(
                    title=title,
                    image_url=img_url,
                    page_url=page_url,
                    tracks=tracks
                ))

        return programs

    def _fetch_tracks(self, session: requests.Session, page_url: str, headers: dict) -> List[AudioDakwahMqTrackEntity]:
        tracks = []
        try:
            sub_resp = session.get(page_url, timeout=5)
            if sub_resp.status_code != 200:
                return tracks
        except Exception as e:
            logger.warning(f"Gagal mengambil track untuk {page_url}: {e}")
            return tracks

        sub_soup = BeautifulSoup(sub_resp.text, 'html.parser')

        post_id = None
        body_element = sub_soup.find('body')
        if body_element:
            for cls in body_element.get('class', []):
                if cls.startswith('postid-'):
                    post_id = cls.split('-')[1]
                    break

        if not post_id:
            shortlink = sub_soup.find('link', rel='shortlink')
            if shortlink and '?p=' in shortlink.get('href', ''):
                post_id = shortlink.get('href').split('?p=')[1]

        if not post_id:
            scripts = sub_soup.find_all('script')
            for s in scripts:
                if s.string and 'var srp_player_params_' in s.string:
                    try:
                        match = re.search(r'var srp_player_params_[a-zA-Z0-9_]+\s*=\s*({.*?});', s.string, re.DOTALL)
                        if match:
                            json_str = match.group(1)
                            player_config = json.loads(json_str)
                            if 'albums' in player_config:
                                post_id = player_config['albums']
                                break
                    except Exception:
                        pass

        if post_id:
            wp_api_base = os.getenv('WP_API_MEDIA_URL')
            wp_api_url = f"{wp_api_base}?parent={post_id}"

            media_headers = headers.copy()
            media_headers.update({'Accept': 'application/json'})

            try:
                api_resp = session.get(wp_api_url, headers=media_headers, timeout=10)
                if api_resp.status_code == 200:
                    media_data = api_resp.json()
                    if isinstance(media_data, list):
                        for item in media_data:
                            if item.get('media_type') == 'file' and 'audio' in item.get('mime_type', ''):
                                mp3_url = item.get('source_url', '')
                                if not mp3_url:
                                    continue

                                title_obj = item.get('title', {})
                                track_title = title_obj.get('rendered', '')
                                if not track_title:
                                    file_name = mp3_url.split('/')[-1]
                                    track_title = file_name.replace('.mp3', '').replace('-', ' ').title()

                                duration_str = ""
                                media_details = item.get('media_details', {})
                                if 'length_formatted' in media_details:
                                    duration_str = media_details['length_formatted']

                                tracks.append(AudioDakwahMqTrackEntity(
                                    title=track_title,
                                    mp3_url=mp3_url,
                                    duration=duration_str
                                ))
            except Exception as e:
                logger.warning(f"Request REST API WP error: {e}")

        return tracks
