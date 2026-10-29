"""
=============================================================================
Program Ekstraksi dan Pengolahan Data Web: Quotes to Scrape (JS Version)
Mata Kuliah: Ekstraksi dan Pengolahan Data Web
Target URL : https://quotes.toscrape.com/js/
=============================================================================
Deskripsi:
Program ini membandingkan teknik web scraping statis (Requests & BeautifulSoup) 
dan dinamis (Selenium WebDriver dengan Explicit Wait) pada website yang 
merender kontennya menggunakan JavaScript (Client-Side Rendering).
=============================================================================
"""

import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================================
# KONFIGURASI PROGRAM
# ============================================================================
BASE_URL = "https://quotes.toscrape.com/js/"
PAGE_TEMPLATE = "https://quotes.toscrape.com/js/page/{}/"
NUM_PAGES = 3

OUTPUT_DIR = "output"
CSV_PATH = os.path.join(OUTPUT_DIR, "kutipan.csv")
SCREENSHOT_PATH = os.path.join(OUTPUT_DIR, "screenshot_quotes.png")


def ensure_output_dir():
    """Membuat folder output jika belum ada."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"[INFO] Direktori '{OUTPUT_DIR}' berhasil dibuat.")


# ============================================================================
# 1. METODE SCRAPING STATIS (REQUESTS + BEAUTIFULSOUP)
# ============================================================================
def scrape_static(num_pages=NUM_PAGES):
    """
    Melakukan scraping statis menggunakan Requests dan BeautifulSoup.
    Tujuan: Menunjukkan apakah elemen kutipan (.quote) dapat diambil dari HTML awal.
    """
    print("\n" + "=" * 65)
    print(">>> 1. MENJALANKAN METODE SCRAPING STATIS (REQUESTS & BEAUTIFULSOUP)")
    print("=" * 65)
    
    start_time = time.perf_counter()
    quotes_data = []

    for page in range(1, num_pages + 1):
        url = PAGE_TEMPLATE.format(page)
        print(f"[*] Mengirim HTTP GET ke: {url}")
        
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Mencari container kutipan berdasarkan class 'quote'
        quote_elements = soup.find_all("div", class_="quote")
        print(f"    - Status HTTP       : {response.status_code}")
        print(f"    - Elemen '.quote'   : Ditemukan {len(quote_elements)} elemen")
        
        for q in quote_elements:
            text = q.find(class_="text").get_text(strip=True) if q.find(class_="text") else ""
            author = q.find(class_="author").get_text(strip=True) if q.find(class_="author") else ""
            tags = [t.get_text(strip=True) for t in q.find_all("a", class_="tag")]
            quotes_data.append({
                "halaman": page,
                "kutipan": text,
                "penulis": author,
                "tag": ", ".join(tags)
            })

    execution_time = time.perf_counter() - start_time
    
    print("-" * 65)
    print(f"[HASIL METODE STATIS]")
    print(f"Total kutipan berhasil diambil : {len(quotes_data)}")
    print(f"Waktu eksekusi metode statis   : {execution_time:.4f} detik")
    print(f"Catatan: Elemen kutipan kosong (0) karena web merender konten via JS.")
    print("-" * 65)
    
    return quotes_data, execution_time


# ============================================================================
# 2. METODE SCRAPING DINAMIS (SELENIUM DENGAN EXPLICIT WAIT)
# ============================================================================
def init_selenium_driver():
    """Menginisialisasi Selenium WebDriver dalam mode headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Mode headless modern Chrome
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Menonaktifkan logging berlebih dari browser
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def scrape_dynamic(num_pages=NUM_PAGES):
    """
    Melakukan scraping dinamis menggunakan Selenium dengan Explicit Wait.
    Mengambil data kutipan, penulis, tag dari minimal 3 halaman,
    serta menyimpan screenshot halaman pertama.
    """
    print("\n" + "=" * 65)
    print(">>> 2. MENJALANKAN METODE SCRAPING DINAMIS (SELENIUM HEADLESS)")
    print("=" * 65)
    
    start_time = time.perf_counter()
    driver = init_selenium_driver()
    quotes_data = []

    try:
        for page in range(1, num_pages + 1):
            url = PAGE_TEMPLATE.format(page)
            print(f"[*] [Selenium] Membuka URL: {url}")
            driver.get(url)

            # Explicit Wait: Menunggu hingga elemen .quote hadir di DOM dan selesai dirender
            wait = WebDriverWait(driver, 15)
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "quote")))
            
            # Ambil screenshot pada halaman pertama
            if page == 1:
                driver.save_screenshot(SCREENSHOT_PATH)
                print(f"    [+] Screenshot halaman 1 disimpan ke: {SCREENSHOT_PATH}")

            # Ekstraksi seluruh elemen kutipan pada halaman yang aktif
            quote_elements = driver.find_elements(By.CLASS_NAME, "quote")
            print(f"    - Berhasil menemukan {len(quote_elements)} elemen kutipan di Halaman {page}")

            for q in quote_elements:
                # Mengambil teks kutipan
                text_elem = q.find_element(By.CLASS_NAME, "text")
                quote_text = text_elem.text.strip() if text_elem else ""

                # Mengambil nama penulis
                author_elem = q.find_element(By.CLASS_NAME, "author")
                author_name = author_elem.text.strip() if author_elem else ""

                # Mengambil daftar tags
                tag_elems = q.find_elements(By.CLASS_NAME, "tag")
                tags = [t.text.strip() for t in tag_elems]

                quotes_data.append({
                    "halaman": page,
                    "kutipan": quote_text,
                    "penulis": author_name,
                    "tag": ", ".join(tags)
                })

    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat scraping dinamis: {e}")
    finally:
        driver.quit()
        print("[*] Browser Selenium ditutup.")

    execution_time = time.perf_counter() - start_time

    print("-" * 65)
    print(f"[HASIL METODE DINAMIS]")
    print(f"Total kutipan berhasil diambil : {len(quotes_data)}")
    print(f"Waktu eksekusi metode dinamis  : {execution_time:.4f} detik")
    print("-" * 65)

    return quotes_data, execution_time


# ============================================================================
# 3. PENYIMPANAN DATA DAN VALIDASI
# ============================================================================
def save_and_validate(quotes_data):
    """Menyimpan data kutipan ke file CSV dan memvalidasi hasilnya."""
    print("\n" + "=" * 65)
    print(">>> 3. MENYIMPAN DATA KE CSV DAN VALIDASI HASIL")
    print("=" * 65)

    if not quotes_data:
        print("[PERINGATAN] Data kutipan kosong. CSV tidak dibuat.")
        return None

    df = pd.DataFrame(quotes_data)
    
    # Simpan dengan UTF-8 with BOM (utf-8-sig) agar karakter khusus/kutipan terbaca baik di Excel
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"[SUCCESS] Data berhasil disimpan ke: {CSV_PATH}")
    print(f"Jumlah baris tersimpan (Total Rows) : {len(df)}")
    print(f"Jumlah kolom tersimpan              : {list(df.columns)}")

    print("\nContoh 5 Baris Pertama Data Hasil Scraping:")
    print("-" * 65)
    for idx, row in df.head(5).iterrows():
        print(f"[{idx + 1}] Hal: {row['halaman']} | Penulis: {row['penulis']}")
        print(f"    Kutipan: {row['kutipan'][:80]}...")
        print(f"    Tags   : {row['tag']}")
    print("-" * 65)

    return df


# ============================================================================
# 4. PERBANDINGAN PERFORMA DAN ANALISIS TEKNIS
# ============================================================================
def display_comparison(t_static, t_dynamic, len_static, len_dynamic):
    """Menampilkan ringkasan perbandingan waktu eksekusi dan analisis teknis."""
    print("\n" + "=" * 65)
    print(">>> 4. PERBANDINGAN WAKTU EKSEKUSI & ANALISIS TEKNIS")
    print("=" * 65)
    print(f"{'Metode':<25} | {'Jumlah Kutipan':<16} | {'Waktu Eksekusi':<15}")
    print("-" * 65)
    print(f"{'Statis (Requests+BS4)':<25} | {len_static:<16} | {t_static:.4f} detik")
    print(f"{'Dinamis (Selenium Headless)':<25} | {len_dynamic:<16} | {t_dynamic:.4f} detik")
    print("-" * 65)
    
    print("\n[PENJELASAN PERBEDAAN WAKTU & HASIL]:")
    print("1. Metode Statis:")
    print("   - Jauh lebih cepat karena hanya mengunduh respons mentah (raw HTML) dari server.")
    print("   - Tidak melakukan inisialisasi browser engine, eksekusi JavaScript, atau pemuatan aset visual.")
    print("   - GAGAL mengambil kutipan (0 kutipan) karena elemen .quote di-generate secara Client-Side.")
    print("2. Metode Dinamis:")
    print("   - Memerlukan waktu lebih lama karena membuka proses Google Chrome di latar belakang (Headless).")
    print("   - Menjalankan V8 JavaScript Engine untuk mengeksekusi skrip jQuery yang menyusun DOM kutipan.")
    print("   - Menggunakan Explicit Wait (WebDriverWait) untuk memastikan elemen benar-benar siap sebelum diekstrak.")
    print("   - BERHASIL mengekstrak seluruh kutipan secara lengkap.")
    print("=" * 65)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main():
    print("=" * 65)
    print("      TUGAS EKSTRAKSI DAN PENGOLAHAN DATA WEB (SCRAPING QUOTES)     ")
    print("=" * 65)
    
    ensure_output_dir()

    # Langkah 1: Scraping Statis
    data_static, time_static = scrape_static(num_pages=NUM_PAGES)

    # Langkah 2: Scraping Dinamis
    data_dynamic, time_dynamic = scrape_dynamic(num_pages=NUM_PAGES)

    # Langkah 3: Simpan dan Validasi Data
    df_result = save_and_validate(data_dynamic)

    # Langkah 4: Tampilkan Perbandingan
    display_comparison(time_static, time_dynamic, len(data_static), len(data_dynamic))

    print("\n[SELESAI] Seluruh rangkaian pengujian scraping berhasil dijalankan.")


if __name__ == "__main__":
    main()
