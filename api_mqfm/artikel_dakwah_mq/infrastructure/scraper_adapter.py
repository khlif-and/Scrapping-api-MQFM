import os
import logging
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from fastapi import HTTPException
from artikel_dakwah_mq.domain.entity import ArtikelDakwahMqEntity, ProgramEntity, ContentEntity
from artikel_dakwah_mq.domain.port import ArtikelDakwahMqScraperPort

load_dotenv()
logger = logging.getLogger(__name__)


class ArtikelDakwahMqScraperAdapter(ArtikelDakwahMqScraperPort):
    def scrape(self) -> ArtikelDakwahMqEntity:
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
        konten_artikel = []

        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')

            program_elements = soup.find_all(string=lambda text: text and '-' in text and ('WIB' in text.upper() or len(text.strip()) <= 15 and text.strip()[0].isdigit()))

            for p in program_elements:
                parent = p.parent
                title_element = parent.find_previous(['h2', 'h3', 'h4', 'strong', 'b'])
                if title_element and title_element.get_text(strip=True):
                    title = title_element.get_text(strip=True)
                    time_schedule = p.strip()
                    if len(time_schedule) > 5 and ('WIB' in time_schedule.upper() or ':' in time_schedule or '.' in time_schedule):
                        program_data = ProgramEntity(program=title, schedule=time_schedule)
                        if program_data not in programs:
                            programs.append(program_data)

            kategori_konten = soup.find_all('a', class_='anwp-link-without-effects')

            contents_dict = {}

            for a in kategori_konten:
                link = a.get('href')
                if not link:
                    continue

                judul = a.get_text(strip=True)
                image_url = None

                container = a.find_parent(['article', 'div', 'li'])
                if container:
                    img_tag = container.find('img')
                    if img_tag:
                        image_url = img_tag.get('src') or img_tag.get('data-src') or img_tag.get('data-lazy-src')

                if link not in contents_dict:
                    contents_dict[link] = {'title': judul, 'link': link, 'image': image_url}
                else:
                    if judul and not contents_dict[link]['title']:
                        contents_dict[link]['title'] = judul
                    if image_url and not contents_dict[link]['image']:
                        contents_dict[link]['image'] = image_url

            for item in contents_dict.values():
                if item['title'] and len(item['title']) > 3:
                    content_item = ContentEntity(title=item['title'], link=item['link'], image=item['image'])
                    if content_item not in konten_artikel:
                        konten_artikel.append(content_item)

        return ArtikelDakwahMqEntity(
            channel_name="102.7 MQFM Bandung",
            tagline="Inspirasi Keluarga Indonesia",
            website="https://mqfmnetwork.com/",
            programs=programs,
            contents=konten_artikel
        )

    def _fetch_html(self, session: requests.Session, url: str) -> str:
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Error koneksi internet atau server MQFM down: {e}")
            raise HTTPException(status_code=503, detail="Gagal menghubungi server MQFM. Pastikan internet Anda aktif atau server tidak down.")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout ke server MQFM: {e}")
            raise HTTPException(status_code=504, detail="Waktu permintaan habis (Timeout) saat mencoba menghubungi server MQFM.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Server MQFM merespon dengan error HTTP: {e}")
            raise HTTPException(status_code=502, detail="Server MQFM bermasalah atau menolak permintaan (HTTP Error).")
        except requests.exceptions.RequestException as e:
            logger.error(f"Gangguan jaringan tidak terduga: {e}")
            raise HTTPException(status_code=500, detail="Terjadi gangguan jaringan saat mengambil data dari MQFM.")
        except Exception as e:
            logger.error(f"Internal server error pada saat scraping: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Terjadi kesalahan internal sistem API pada saat web scraping.")
