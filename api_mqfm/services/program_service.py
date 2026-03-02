import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List
from entities.program_entity import ProgramEntity

load_dotenv()

class ProgramService:
    @staticmethod
    def scrape_program_on_air() -> List[ProgramEntity]:
        url = os.getenv('MQFM_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        programs = []
        
        carousel_imgs = soup.select('.elementor-image-carousel .swiper-slide img')
        
        try:
            with open("debug_programs.txt", "w", encoding="utf-8") as f:
                for idx, img in enumerate(carousel_imgs):
                    f.write(f"IMG {idx}:\n")
                    f.write(f"  SRC: {img.get('src')}\n")
                    f.write(f"  ALT: {img.get('alt')}\n")
                    f.write(f"  TITLE_ATTR: {img.get('title')}\n\n")
        except:
            pass
            
        for img in carousel_imgs:
            src = img.get('src')
            if not src:
                continue
                
            alt_text = img.get('alt', '')
            title = alt_text.replace('PROGRAM UNGGULAN MQFM', '').strip()
            
            if not title:
                filename = src.split('/')[-1]
                title = filename.replace('-', ' ').replace('.png', '').replace('.jpg', '').strip()
            
            programs.append(ProgramEntity(
                title=title,
                image_url=src
            ))
            
        return programs
