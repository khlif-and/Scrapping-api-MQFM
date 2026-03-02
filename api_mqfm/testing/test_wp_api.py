import requests
import json

def test_api():
    # ID for Solusi Quran based on debug
    album_id = "7362"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    
    # Let's try the built-in WordPress REST API for sonaar
    urls_to_test = [
         f"https://mqfmnetwork.com/wp-json/wp/v2/sr_playlist/{album_id}",
         f"https://mqfmnetwork.com/wp-json/sonaar/v1/playlist/{album_id}",
         f"https://mqfmnetwork.com/?load=playlist.json&albums={album_id}&feed=1",
         f"https://mqfmnetwork.com/wp-json/wp/v2/media?parent={album_id}"
    ]
    
    session = requests.Session()
    session.headers.update(headers)
    if 'Accept-Encoding' in session.headers:
        del session.headers['Accept-Encoding']
        
    for url in urls_to_test:
        print(f"\nTesting: {url}")
        try:
            resp = session.get(url, timeout=5)
            print("Status:", resp.status_code)
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    # Just print snippet
                    print("JSON Length:", len(str(data)))
                    if isinstance(data, list) and len(data) > 0:
                        print("Keys:", data[0].keys())
                    elif isinstance(data, dict):
                         print("Keys:", data.keys())
                except:
                    print("Response length:", len(resp.text))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    test_api()
