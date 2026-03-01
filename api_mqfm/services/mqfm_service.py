import requests
from bs4 import BeautifulSoup
from models.mqfm_model import MqfmData, ProgramItem, ContentItem

class MqfmService:
    @staticmethod
    def scrape_data() -> MqfmData:
        url = 'https://mqfmnetwork.com/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        programs = []
        program_elements = soup.find_all(string=lambda text: text and '-' in text and ('WIB' in text.upper() or len(text.strip()) <= 15 and text.strip()[0].isdigit()))
        
        for p in program_elements:
            parent = p.parent
            title_element = parent.find_previous(['h2', 'h3', 'h4', 'strong', 'b'])
            if title_element and title_element.get_text(strip=True):
                title = title_element.get_text(strip=True)
                time_schedule = p.strip()
                if len(time_schedule) > 5 and ('WIB' in time_schedule.upper() or ':' in time_schedule or '.' in time_schedule):
                    program_data = ProgramItem(program=title, schedule=time_schedule)
                    if program_data.model_dump() not in [prog.model_dump() for prog in programs]:
                        programs.append(program_data)

        kategori_konten = soup.find_all('a', class_='anwp-link-without-effects')
        
        contents_dict = {}
        
        for a in kategori_konten:
            link = a.get('href')
            if not link:
                continue
                
            judul = a.get_text(strip=True)
            image_url = None
            
            # Cari dari parent container
            container = a.find_parent(['article', 'div', 'li'])
            if container:
                img_tag = container.find('img')
                if img_tag:
                    image_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src')
                    
            if link not in contents_dict:
                contents_dict[link] = {'title': judul, 'link': link, 'image': image_url}
            else:
                # Timpa dengan data yang lebih lengkap jika ada
                if judul and not contents_dict[link]['title']:
                    contents_dict[link]['title'] = judul
                if image_url and not contents_dict[link]['image']:
                    contents_dict[link]['image'] = image_url

        konten_artikel = []
        for item in contents_dict.values():
            if item['title'] and len(item['title']) > 3: # Pastikan judulnya valid (bukan sekedar spasi)
                content_item = ContentItem(title=item['title'], link=item['link'], image=item['image'])
                if content_item.model_dump() not in [c.model_dump() for c in konten_artikel]:
                    konten_artikel.append(content_item)

        return MqfmData(
            channel_name="102.7 MQFM Bandung",
            tagline="Inspirasi Keluarga Indonesia",
            website="https://mqfmnetwork.com/",
            programs=programs,
            contents=konten_artikel
        )
