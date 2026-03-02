import requests
import re
import json

def check_youtube_live(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    print(f"Checking URL: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        html = resp.text
        
        # Youtube puts a lot of metadata in ytInitialPlayerResponse
        match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
        if match:
            data = json.loads(match.group(1))
            video_details = data.get('videoDetails', {})
            is_live = video_details.get('isLiveContent', False)
            title = video_details.get('title', 'Unknown')
            
            print(f"Title: {title}")
            print(f"Is Live Content: {is_live}")
            
            # Additional check:
            # if isLiveContent is True, is it currently live, or was it a past stream?
            # We can check microformat -> playerMicroformatRenderer -> liveBroadcastDetails -> isLiveNow
            try:
                microformat = data.get('microformat', {}).get('playerMicroformatRenderer', {})
                live_details = microformat.get('liveBroadcastDetails', {})
                is_live_now = live_details.get('isLiveNow', False)
                print(f"Is Live NOW: {is_live_now}")
            except Exception as e:
                print(f"Error checking isLiveNow: {e}")
                
            return
            
        print("Could not find ytInitialPlayerResponse")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_youtube_live("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Not live
    print("---")
    check_youtube_live("https://www.youtube.com/channel/UCiT19P1_P2C9pS5v9L9_vGw/live") # Need MQFM URL... wait, I'll test the one from the page
