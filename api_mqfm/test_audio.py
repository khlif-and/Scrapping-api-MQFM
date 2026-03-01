import requests
import re
import json

def test_fetch():
    url = "https://mqfmnetwork.com/cahaya-tauhiid-kh-abdullah-gymnastiar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    if 'Accept-Encoding' in session.headers:
        del session.headers['Accept-Encoding']
        
    print("1. Fetching subpage HTML...")
    try:
        res = session.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print("Failed to fetch subpage:", e)
        return
        
    html = res.text
    print("Subpage loaded. Panjang HTML:", len(html))
    
    print("\n2. Mengekstrak variabel Sonaar Player dari tag <script>...")
    scripts = re.findall(r'<script.*?>.*?</script>', html, re.DOTALL | re.IGNORECASE)
    
    tracks_found = False
    for s in scripts:
        if 'var srp_player_params_' in s:
            print("=> Menemukan blok script Sonaar Config!")
            try:
                # Coba cari JSON config-nya
                match = re.search(r'var srp_player_params_[a-zA-Z0-9_]+\s*=\s*({.*?});', s, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    player_config = json.loads(json_str)
                    
                    if 'tracks' in player_config and isinstance(player_config['tracks'], list):
                        tracks = player_config['tracks']
                        print(f"\n[SUKSES BINGO!] Berhasil mengekstrak {len(tracks)} tracks langsung dari HTML!")
                        for i, t in enumerate(tracks[:3]): # Tampilkan 3 pertama
                            print(f"   Track {i+1}: {t.get('track_title')} -> {t.get('mp3')}")
                        if len(tracks) > 3:
                            print(f"   ... dan {len(tracks)-3} tracks lainnya.")
                        tracks_found = True
                        break
            except Exception as e:
                print("Error parsing srp_player_params_ json:", e)
                
    if not tracks_found:
        print("\n[GAGAL] Tidak dapat menemukan array 'tracks' di dalam HTML.")

if __name__ == "__main__":
    test_fetch()
