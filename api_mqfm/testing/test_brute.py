import requests
import re
import json

def brute_force_search():
    url = "https://mqfmnetwork.com/cahaya-tauhiid-kh-abdullah-gymnastiar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    if 'Accept-Encoding' in session.headers:
        del session.headers['Accept-Encoding']
        
    res = session.get(url, timeout=10)
    html = res.text
    
    print("Page length:", len(html))
    
    # Brute force search for ANY .mp3 URL in the entire HTML document
    mp3_links = re.findall(r'(https?://[^\s"\'<>]+?\.mp3)', html, re.IGNORECASE)
    
    if mp3_links:
        print(f"BINGO! Found {len(mp3_links)} direct MP3 links in HTML:")
        unique_links = list(set(mp3_links))
        for link in unique_links[:10]:
            print(" -", link)
    else:
        print("NO .mp3 links found in the raw HTML at all!")
        
        # If no mp3s, let's search for sonaar ajax actions in the JS files
        js_files = re.findall(r'src="(https?://[^"]+\.js[^"]*)"', html)
        sonaar_js = [js for js in js_files if 'sonaar' in js.lower()]
        print("\nFound Sonaar JS files:")
        for js in sonaar_js:
            print(js)
            try:
                js_res = session.get(js)
                actions = re.findall(r'action\s*:\s*["\']([^"\']+)["\']', js_res.text)
                if actions:
                    print("  -> Actions found in JS:", set(actions))
            except:
                pass


if __name__ == "__main__":
    brute_force_search()
