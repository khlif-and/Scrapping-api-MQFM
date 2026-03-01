import requests
import re
from bs4 import BeautifulSoup

def find_duration_in_html():
    url = "https://mqfmnetwork.com/solusi-quran/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    
    session = requests.Session()
    session.headers.update(headers)
    if 'Accept-Encoding' in session.headers:
        del session.headers['Accept-Encoding']
        
    resp = session.get(url, headers=headers)
    html = resp.text
    
    print("Page Fetched:", len(html))
    
    # Let's search for "Al-Baqarah" or "Solusi" and see how Sonaar structures the tracklist
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Search for elements containing the track title
    elements = soup.find_all(string=re.compile(r'Solusi Quran Surat Al-Baqarah Bagian 4', re.IGNORECASE))
    for el in elements:
        parent = el.parent
        print("MATCHED TEXT:", el.strip())
        print("PARENT TAG:", parent.name, parent.attrs)
        
        # Go up a few levels to see the container
        container = parent
        for _ in range(3):
            if container and container.parent:
                container = container.parent
        
        print("CONTAINER HTML PREVIEW:\n", str(container)[:500])
        print("---")
        
    # 2. Search for the specific '3:24' string
    durations = soup.find_all(string=re.compile(r'3:24'))
    for d in durations:
        print("MATCHED DURATION:", d.strip())
        print("PARENT TAG:", d.parent.name, d.parent.attrs)
        print("---")
        
    # 3. Are there any sonaar JSON attributes in data-attributes?
    sonaar_tags = soup.find_all(attrs={"data-tracks": True})
    for t in sonaar_tags:
         print("FOUND DATA-TRACKS!")
         print(t['data-tracks'][:500])

if __name__ == "__main__":
    find_duration_in_html()
