import requests
from bs4 import BeautifulSoup
from models.youtube_model import YoutubeStreamInfo

class YoutubeService:
    @staticmethod
    def scrape_youtube_stream() -> YoutubeStreamInfo:
        url = 'https://mqfmnetwork.com/streaming/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        youtube_url = None
        title = None
        
        # Cari iframe YouTube
        iframes = soup.find_all('iframe')
        for iframe in iframes:
            src = iframe.get('src')
            if src and ('youtube.com' in src or 'youtu.be' in src):
                # Konversi URL embed menjadi URL yang bisa dibuka langsung (mengatasi Error 153)
                if '/embed/live_stream?channel=' in src:
                    channel_id = src.split('channel=')[1].split('&')[0]
                    youtube_url = f"https://www.youtube.com/channel/{channel_id}/live"
                elif '/embed/' in src:
                    video_id = src.split('/embed/')[1].split('?')[0]
                    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                else:
                    youtube_url = src
                
                # Ambil judul video dari atribut title jika ada
                title = iframe.get('title')
                break
                
        # Jika tidak ketemu iframe, coba cari link YouTube langsung
        if not youtube_url:
            links = soup.find_all('a')
            for a in links:
                href = a.get('href')
                if href and ('youtube.com/watch' in href or 'youtube.com/live' in href or 'youtu.be' in href):
                    # Pastikan ini konteks live streaming
                    parent_text = a.find_parent().get_text(strip=True).upper()
                    if 'LIVE' in parent_text or 'STREAMING' in parent_text:
                        youtube_url = href
                        title = a.get_text(strip=True) or (a.get('title'))
                        if title and len(title) > 3:
                            break
                        
        if not title and youtube_url:
            title = "MQFM Live YouTube Stream"
            
        # =========================================================
        # VALIDASI STATUS LIVE ASLI DI YOUTUBE
        # =========================================================
        if youtube_url:
            try:
                import re
                import json
                yt_resp = requests.get(youtube_url, headers=headers, timeout=10)
                yt_html = yt_resp.text
                
                is_currently_live = False
                
                # Ekstrak metadata jeroan YouTube Player
                match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', yt_html)
                if match:
                    data = json.loads(match.group(1))
                    
                    video_details = data.get('videoDetails', {})
                    if video_details.get('isLiveContent', False):
                        # Video adalah tipe siaran langsung, mari cek apakah MANTAN live atau SEDANG live
                        microformat = data.get('microformat', {}).get('playerMicroformatRenderer', {})
                        live_details = microformat.get('liveBroadcastDetails', {})
                        
                        is_currently_live = live_details.get('isLiveNow', False)
                        
                        # Timpa judul dari MQFM dengan judul asli YouTube yang terupdate
                        yt_title = video_details.get('title', '')
                        if yt_title:
                            title = yt_title

                # Jika tidak sedang live (mungkin hanya VOD/Replay dari siaran lama), batalkan linknya
                if not is_currently_live:
                    youtube_url = None
                    title = None
            except Exception as e:
                # Jika terjadi error parsing YT, biarkan link YT kosong agar 404 ketrigger di controller
                youtube_url = None
                title = None

        return YoutubeStreamInfo(
            youtube_url=youtube_url,
            title=title
        )
