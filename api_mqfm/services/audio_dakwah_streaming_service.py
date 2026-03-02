import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from entities.audio_dakwah_streaming_entity import AudioDakwahStreamingEntity
from repositories.audio_dakwah_streaming_repository import AudioDakwahStreamingRepository

load_dotenv()

class AudioDakwahStreamingService:
    @staticmethod
    def scrape_audio_dakwah_streaming() -> AudioDakwahStreamingEntity:
        url = os.getenv('AUDIO_DAKWAH_STREAMING_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }
        
        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']
            
        html_content = AudioDakwahStreamingRepository.get_streaming_html(session, url)
        
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
                    parent = el.parent
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

            time_elements = soup.find_all(string=lambda text: text and '-' in text and ('WIB' in text.upper() or len(text.strip()) <= 15 and text.strip()[0].isdigit() and ':' in text))
            
            wp_ajax_url = os.getenv('WP_AJAX_URL')
            
            payload = {
                'action': 'show_time_curd',
                'crud-action': 'read',
                'read-type': 'current'
            }
            
            schedule_data = AudioDakwahStreamingRepository.get_wp_ajax_schedule(session, wp_ajax_url, payload)
                    
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
