import requests
from bs4 import BeautifulSoup
import json

def scrape_mqfm_programs():
    url = 'https://mqfmnetwork.com/'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    try:
        print(f"Mengambil data program dari {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ekstrak jadwal siaran/program
        # Mencari teks yang mengandung informasi jam siaran (misalnya 05.00 - 06.00)
        programs = []
        
        # Strategi 1: Mencari elemen yang biasanya berisi jadwal (contoh: di dalam widget Elementor)
        program_elements = soup.find_all(string=lambda text: text and '-' in text and ('WIB' in text.upper() or len(text.strip()) <= 15 and text.strip()[0].isdigit()))
        
        for p in program_elements:
            parent = p.parent
            # Mencari elemen heading terdekat yang mungkin merupakan judul program
            title_element = parent.find_previous(['h2', 'h3', 'h4', 'strong', 'b'])
            
            if title_element and title_element.get_text(strip=True):
                title = title_element.get_text(strip=True)
                time_schedule = p.strip()
                
                # Filter agar tidak memasukkan data yang salah (misal nomor telepon DLL)
                if len(time_schedule) > 5 and ('WIB' in time_schedule.upper() or ':' in time_schedule or '.' in time_schedule):
                    program_data = {'program': title, 'jadwal': time_schedule}
                    if program_data not in programs:
                        programs.append(program_data)

        # Jika data masih kosong, kita coba ekstrak blok artikel Khazanah MQ sebagai "konten"
        kategori_konten = soup.find_all('a', class_='anwp-link-without-effects')
        konten_artikel = []
        for a in kategori_konten:
            judul = a.get_text(strip=True)
            link = a.get('href')
            if judul and link and {'judul': judul, 'link': link} not in konten_artikel:
                konten_artikel.append({'judul': judul, 'link': link})

        # Menampilkan Data
        print("\n=== INFORMASI SALURAN RADIO ===")
        print("Nama Saluran: 102.7 MQFM Bandung")
        print("Tagline: Inspirasi Keluarga Indonesia")
        print("Website: https://mqfmnetwork.com/")
        
        print("\n=== JADWAL PROGRAM RADIO ===")
        if programs:
            for i, p in enumerate(programs, 1):
                print(f"{i}. {p['program']} ({p['jadwal']})")
        else:
            print("Jadwal program spesifik tidak ditemukan di halaman utama secara langsung.")
            print("Biasanya jadwal siaran live dapat dilihat secara dinamis di halaman web atau melalui aplikasi khusus.")

        print(f"\n=== KONTEN/ARTIKEL DITEMUKAN ({len(konten_artikel)}) ===")
        for i, k in enumerate(konten_artikel, 1):
            print(f"{i}. {k['judul']}")
            print(f"   Link: {k['link']}")
            if i >= 10: # Batasi tampilan hanya 10 konten pertama
                print(f"   ... dan {len(konten_artikel) - 10} konten lainnya.")
                break

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengambil halaman web: {e}")

if __name__ == "__main__":
    scrape_mqfm_programs()
