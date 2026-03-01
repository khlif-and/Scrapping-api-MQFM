import logging
import requests
from bs4 import BeautifulSoup
from typing import List
from models.audio_model import AudioProgramModel, AudioTrackModel

logger = logging.getLogger(__name__)

class AudioService:
    @staticmethod
    def _get_mp3_duration(url: str, session: requests.Session) -> str:
        try:
            # Karena mendownload partial (chunk) dengan Mutagen terbukti gagal 
            # (hanya membaca 1 detik pertama), kita menggunakan perhitungan standar
            # durasi berdasarkan besar total file (Content-Length) HTTP Head.
            head_resp = session.head(url, timeout=3)
            content_length = int(head_resp.headers.get('Content-Length', 0))
            if content_length > 0:
                # Podcast MQFM umumnya direkam dengan bitrate sangat rendah (mono voice)
                # Estimasi paling akurat untuk MP3 mereka adalah 48 kbps
                estimated_kbps = 48
                bytes_per_second = (estimated_kbps * 1000) / 8
                total_seconds = int(content_length / bytes_per_second)
                
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                
                if hours > 0:
                    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                else:
                    return f"{minutes:02d}:{seconds:02d}"
                    
            return ""
        except Exception as e:
            logger.warning(f"Gagal estimasi durasi MP3 {url}: {e}")
            return ""

    @staticmethod
    def scrape_audio_on_demand() -> List[AudioProgramModel]:
        url = 'https://mqfmnetwork.com/audio-on-demand/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # Memaksa server hanya mengirimkan GZIP atau Plain, karena Brotli (br) server MQFM rusak (decoder error)
            'Accept-Encoding': 'gzip, deflate'
        }
        
        session = requests.Session()
        session.headers.update(headers)
        # Force remove Accept-Encoding to prevent requests from automatically adding 'br' (Brotli)
        # which causes "decoder process called with data when can_accept_more_data() is False" on this specific server
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']
        
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
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
                
                tracks = []
                try:
                    sub_resp = session.get(page_url, timeout=5)
                    if sub_resp.status_code == 200:
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
                             # Coba ekstrak dari srp_player_params jika body class gagal
                             scripts = sub_soup.find_all('script')
                             import re
                             import json
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
                                     except:
                                         pass
                                         
                        if post_id:
                            # Menggunakan Endpoint WordPress REST API Media Asli
                            # Endpoint ini mengembalikan semua media file (MP3) attachment beserta durasi aslinya
                            wp_api_url = f"https://mqfmnetwork.com/wp-json/wp/v2/media?parent={post_id}"
                            
                            media_headers = headers.copy()
                            media_headers.update({
                                'Accept': 'application/json'
                            })
                            
                            api_resp = session.get(wp_api_url, headers=media_headers, timeout=10)
                            if api_resp.status_code == 200:
                                try:
                                    media_data = api_resp.json()
                                    if isinstance(media_data, list):
                                        for item in media_data:
                                            # Memastikan item adalah file audio
                                            if item.get('media_type') == 'file' and 'audio' in item.get('mime_type', ''):
                                                mp3_url = item.get('source_url', '')
                                                if not mp3_url:
                                                    continue
                                                    
                                                # Ambil judul asli dari database WordPress
                                                title_obj = item.get('title', {})
                                                track_title = title_obj.get('rendered', '')
                                                if not track_title:
                                                     file_name = mp3_url.split('/')[-1]
                                                     track_title = file_name.replace('.mp3', '').replace('-', ' ').title()
                                                
                                                # Ambil durasi pasti yang tersimpan di meta WP (format MM:SS)
                                                duration_str = ""
                                                media_details = item.get('media_details', {})
                                                if 'length_formatted' in media_details:
                                                    duration_str = media_details['length_formatted']
                                                    
                                                tracks.append(AudioTrackModel(
                                                    title=track_title,
                                                    mp3_url=mp3_url,
                                                    duration=duration_str
                                                ))
                                except Exception as e:
                                    logger.warning(f"Gagal parse REST API WP untuk {post_id}: {e}")
                            else:
                                 logger.warning(f"REST API WP menolak request: {api_resp.status_code}")
                        else:
                            logger.warning(f"Gagal menemukan Post ID di halaman: {page_url}")
                except Exception as e:
                    logger.warning(f"Gagal mengambil track untuk {page_url}: {e}")
                    
                programs.append(AudioProgramModel(
                    title=title,
                    image_url=img_url,
                    page_url=page_url,
                    tracks=tracks
                ))
                
        return programs
