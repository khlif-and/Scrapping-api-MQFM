import requests
import re
import json

def dump_script():
    url = "https://mqfmnetwork.com/cahaya-tauhiid-kh-abdullah-gymnastiar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    if 'Accept-Encoding' in session.headers:
        del session.headers['Accept-Encoding']
        
    print("Fetching subpage HTML...")
    res = session.get(url, timeout=10)
    html = res.text
    
    scripts = re.findall(r'<script.*?>.*?</script>', html, re.DOTALL | re.IGNORECASE)
    
    for idx, s in enumerate(scripts):
        if 'var srp_player_params_' in s:
            print(f"Found srp_player_params_ in script block {idx}!")
            with open("dump_srp_script.txt", "w", encoding="utf-8") as f:
                f.write(s)
            print("Dumped full script block to dump_srp_script.txt")
            
        if 'var sonaar_music' in s:
             with open("dump_sonaar_script.txt", "w", encoding="utf-8") as f:
                f.write(s)

if __name__ == "__main__":
    dump_script()
