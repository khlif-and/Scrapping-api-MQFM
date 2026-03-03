import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List
from entities.program_and_adds_entity import ProgramAndAddsEntity
from repositories.program_and_adds_repository import ProgramAndAddsRepository

load_dotenv()

class ProgramAndAddsService:
    @staticmethod
    def scrape_program_and_adds() -> List[ProgramAndAddsEntity]:
        url = os.getenv('MQFM_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }
        
        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']
            
        html_content = ProgramAndAddsRepository.get_mqfm_html(session, url)
        
        programs = []
        
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            carousel_imgs = soup.select('.elementor-image-carousel .swiper-slide img')
                
            for img in carousel_imgs:
                src = img.get('src')
                if not src:
                    continue
                    
                alt_text = img.get('alt', '')
                title = alt_text.replace('PROGRAM UNGGULAN MQFM', '').strip()
                
                if not title:
                    filename = src.split('/')[-1]
                    title = filename.replace('-', ' ').replace('.png', '').replace('.jpg', '').strip()
                
                programs.append(ProgramAndAddsEntity(
                    title=title,
                    image_url=src
                ))
                
        return programs
