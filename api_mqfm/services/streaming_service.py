import requests
from bs4 import BeautifulSoup
from models.streaming_model import StreamingInfo

class StreamingService:
    @staticmethod
    def scrape_streaming_data() -> StreamingInfo:
        url = 'https://mqfmnetwork.com/streaming/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        current_program = None
        schedule = None
        audio_url = None
        
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
        
        # Ekstrak data dari widget jadwal melalui API Endpoint WordPress AJAX
        wp_ajax_url = "https://mqfmnetwork.com/wp-admin/admin-ajax.php"
        
        up_next_program = None
        up_next_schedule = None
        
        try:
            # Sesuai inspeksi, plugin mengirim POST request dengan payload berikut:
            payload = {
                'action': 'show_time_curd',
                'crud-action': 'read',
                'read-type': 'current'
            }
            
            api_response = requests.post(wp_ajax_url, data=payload, headers=headers, timeout=5)
                
            if api_response.status_code == 200:
                schedule_data = api_response.json()
                
                # Format response dari plugin:
                # {"current_show":{"id":"...","show_name":"MQ SORE","start_time":"15:00:00","end_time":"16:00:00"}, "upcoming_show":{...}}
                
                if isinstance(schedule_data, dict):
                    current_show = schedule_data.get('current_show')
                    if isinstance(current_show, dict):
                         current_program = current_show.get('show_name', current_program)
                         start = current_show.get('start_time', '')[:5] # ambil HH:MM
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
                             
        except Exception as e:
            import logging
            logging.warning(f"Failed to fetch schedule API from URL. Fallback invoked. Error: {e}")
        
        # Jika API AJAX gagal atau mengembalikan data kosong, fallback ke default
        if not current_program or current_program == "•Live Streaming" or current_program == "Live StreamingAudio on Demand" or "Live Streaming" in current_program:
            current_program = "Live On Air 102.7 MQFM Bandung"
            
        if not schedule:
            schedule = "On Air 24 Jam"
                
        return StreamingInfo(
            current_program=current_program,
            schedule=schedule,
            up_next_program=up_next_program,
            up_next_schedule=up_next_schedule,
            audio_url=audio_url
        )
