import os
import logging
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from typing import List
from fastapi import HTTPException
from program_and_adds.domain.entity import ProgramAndAddsEntity
from program_and_adds.domain.port import ProgramAndAddsScraperPort

load_dotenv()
logger = logging.getLogger(__name__)


class ProgramAndAddsScraperAdapter(ProgramAndAddsScraperPort):
    def scrape(self) -> List[ProgramAndAddsEntity]:
        url = os.getenv('MQFM_URL')
        headers = {
            'User-Agent': os.getenv('USER_AGENT'),
            'Accept-Encoding': os.getenv('ACCEPT_ENCODING')
        }

        session = requests.Session()
        session.headers.update(headers)
        if 'Accept-Encoding' in session.headers:
            del session.headers['Accept-Encoding']

        html_content = self._fetch_html(session, url)
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

                programs.append(ProgramAndAddsEntity(title=title, image_url=src))

        return programs

    def _fetch_html(self, session: requests.Session, url: str) -> str:
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error koneksi internet saat mengambil Program On Air: {e}")
            raise HTTPException(status_code=503, detail="Gagal menghubungi server MQFM. Pastikan internet Anda aktif.")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout saat mengambil Program On Air: {e}")
            raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout).")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error saat mengambil Program On Air: {e}")
            raise HTTPException(status_code=502, detail="Server MQFM bermasalah atau menolak permintaan (HTTP Error).")
        except requests.exceptions.RequestException as e:
            logger.error(f"Gangguan jaringan tidak terduga: {e}")
            raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat memuat Program On Air.")
        except Exception as e:
            logger.error(f"Internal server error pada Program On Air scraping: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal pada saat web scraping Program On Air.")
