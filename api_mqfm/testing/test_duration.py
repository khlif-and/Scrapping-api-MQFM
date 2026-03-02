import requests
import io
import time
from mutagen.mp3 import MP3

def test_duration():
    url = "https://mqfmnetwork.com/wp-content/uploads/2023/10/Amalan-Utama-Yang-Membuat-HIdup-Bahagia-dan-Mulia.mp3"
    
    # 1. Test Mutagen with chunk
    print("Testing Mutagen with 64KB chunk...")
    headers = {'Range': 'bytes=0-65535'}
    try:
        resp = requests.get(url, headers=headers, stream=True)
        file_like = io.BytesIO(resp.content)
        audio = MP3(file_like)
        print(f"Mutagen Length: {audio.info.length} seconds")
        print(f"Mutagen Bitrate: {audio.info.bitrate}")
    except Exception as e:
        print(f"Mutagen error: {e}")
        
    print("\n---")
    
    # 2. Test Fallback File Size calculation
    print("Testing Fallback calculation...")
    try:
        head_resp = requests.head(url)
        content_length = int(head_resp.headers.get('Content-Length', 0))
        print(f"Content-Length: {content_length} bytes")
        
        # Test 64kbps duration
        estimated_kbps = 64
        bytes_per_second = (estimated_kbps * 1000) / 8
        total_seconds = int(content_length / bytes_per_second)
        
        print(f"Calculated Length (64kbps): {total_seconds} seconds")
        
        # Format
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        print(f"Formatted: {hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"Formatted: {minutes:02d}:{seconds:02d}")
        
    except Exception as e:
        print(f"Fallback error: {e}")

if __name__ == "__main__":
    test_duration()
