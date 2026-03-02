import os
import re
import json
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from entities.youtube_dakwah_streaming_entity import YoutubeDakwahStreamingEntity
from repositories.youtube_dakwah_streaming_repository import YoutubeDakwahStreamingRepository

load_dotenv()

class YoutubeDakwahStreamingService:
    @staticmethod
    def scrape_youtube_dakwah_streaming() -> YoutubeDakwahStreamingEntity:
        url = os.getenv('AUDIO_DAKWAH_STREAMING_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }
        
        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']
            
        html_content = YoutubeDakwahStreamingRepository.get_youtube_html(session, url)
        
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
                yt_html = YoutubeDakwahStreamingRepository.validate_youtube_live_status(session, youtube_url)
                if yt_html:
                    is_currently_live = False
                    
                    match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', yt_html)
                    if match:
                        data = json.loads(match.group(1))
                        
                        video_details = data.get('videoDetails', {})
                        if video_details.get('isLiveContent', False):
                            microformat = data.get('microformat', {}).get('playerMicroformatRenderer', {})
                            live_details = microformat.get('liveBroadcastDetails', {})
                            
                            is_currently_live = live_details.get('isLiveNow', False)
                            
                            yt_title = video_details.get('title', '')
                            if yt_title:
                                title = yt_title

                    if not is_currently_live:
                        youtube_url = None
                        title = None
                else:
                    youtube_url = None
                    title = None

        return YoutubeDakwahStreamingEntity(
            youtube_url=youtube_url,
            title=title
        )
