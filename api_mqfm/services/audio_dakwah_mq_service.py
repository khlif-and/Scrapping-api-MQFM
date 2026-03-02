import logging
import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List
from entities.audio_dakwah_mq_entity import AudioDakwahMqProgramEntity, AudioDakwahMqTrackEntity

load_dotenv()
logger = logging.getLogger(__name__)

class AudioDakwahMqService:
    @staticmethod
    def _get_mp3_duration(url: str, session: requests.Session) -> str:
        try:
            head_resp = session.head(url, timeout=3)
            content_length = int(head_resp.headers.get('Content-Length', 0))
            if content_length > 0:
                estimated_kbps = int(os.getenv('AUDIO_ESTIMATED_KBPS', 48))
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
    def scrape_audio_dakwah_mq() -> List[AudioDakwahMqProgramEntity]:
        url = os.getenv('AUDIO_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }
        
        session = requests.Session()
        session.headers.update(headers)
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
                from repositories.audio_dakwah_mq_repository import AudioDakwahMqRepository
                sub_page_html = AudioDakwahMqRepository.get_sub_page_html(session, page_url)
                if sub_page_html:
                    sub_soup = BeautifulSoup(sub_page_html, 'html.parser')
                    
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
                        wp_api_base = os.getenv('WP_API_MEDIA_URL')
                        wp_api_url = f"{wp_api_base}?parent={post_id}"
                        
                        media_headers = headers.copy()
                        media_headers.update({
                            'Accept': 'application/json'
                        })
                        
                        media_data = AudioDakwahMqRepository.get_wp_media_json(session, wp_api_url, media_headers)
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
                    
                programs.append(AudioDakwahMqProgramEntity(
                    title=title,
                    image_url=img_url,
                    page_url=page_url,
                    tracks=tracks
                ))
                
        return programs
