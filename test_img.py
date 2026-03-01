import requests
from bs4 import BeautifulSoup

def test_scrape():
    url = 'https://mqfmnetwork.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    articles = soup.find_all('article')
    print(f"Total articles found: {len(articles)}")
    
    for i, article in enumerate(articles[:5]):
        print(f"\n--- Article {i+1} ---")
        title_link = article.find('a', class_='anwp-link-without-effects')
        if title_link:
            print(f"Title: {title_link.get_text(strip=True)}")
        
        img = article.find('img')
        if img:
            print(f"Img src: {img.get('src')}")
            print(f"Img data-src: {img.get('data-src')}")
            print(f"Img srcset: {img.get('srcset')}")
            print(f"Img class: {img.get('class')}")
        else:
            print("No <img> tag found in this <article> element.")
            # Let's print the raw HTML of the article to see what's actually there
            print("Raw HTML:", str(article)[:500])

if __name__ == "__main__":
    test_scrape()
