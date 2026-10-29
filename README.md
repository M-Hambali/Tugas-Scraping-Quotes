# Tugas Web Scraping: Quotes to Scrape (JS Version)

Repositori ini berisi implementasi tugas mata kuliah **Ekstraksi dan Pengolahan Data Web** untuk melakukan komparasi antara teknik web scraping **Statis** (*Requests + BeautifulSoup*) dan **Dinamis** (*Selenium WebDriver Headless*) pada situs web berbasis JavaScript (*Client-Side Rendering*).

- **Objek Target:** [https://quotes.toscrape.com/js/](https://quotes.toscrape.com/js/)
- **Lingkungan Uji:** Windows 11, Python 3.13, Google Chrome, Virtual Environment (`venv`).

---

## 📁 Struktur Direktori Proyek

```text
Tugas Scraping Quotes/
│
├── .venv/                      # Virtual environment Python (lokal)
├── output/                     # Berkas keluaran program
│   ├── kutipan.csv             # Data hasil scraping (30 baris data UTF-8-SIG)
│   ├── screenshot_quotes.png   # Screenshot halaman 1 hasil render Selenium
│   └── laporan_praktikum.md    # Laporan praktikum lengkap (1–2 halaman)
│
├── main.py                     # Skrip utama scraping & pengujian
├── requirements.txt            # Daftar pustaka dependensi proyek
├── .gitignore                  # Berkas pengabaian Git (venv, cache, dll)
└── README.md                   # Dokumentasi panduan proyek
```

---

## 🛠️ Prasyarat Sistem

1. **Sistem Operasi:** Windows 10/11 (64-bit).
2. **Python:** Python 3.10 ke atas (diuji pada Python 3.13.7).
3. **Google Chrome:** Terpasang pada direktori standar Windows (`C:\Program Files\Google\Chrome\Application\chrome.exe`).
4. **Selenium Manager:** Sudah terintegrasi langsung di dalam pustaka Selenium 4, sehingga **tidak perlu** mengunduh ChromeDriver secara manual.

---

## 🚀 Panduan Instalasi & Menjalankan Program

Buka terminal **PowerShell** atau **Command Prompt** di direktori proyek ini, lalu ikuti langkah berikut:

### 1. Buat dan Aktifkan Virtual Environment
```powershell
# Membuat virtual environment
python -m venv .venv

# Mengaktifkan virtual environment di Windows PowerShell
.\.venv\Scripts\Activate.ps1
```
*(Catatan: Jika muncul error permission execution policy di PowerShell, jalankan `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`)*

### 2. Instal Dependensi
```powershell
pip install -r requirements.txt
```

### 3. Jalankan Program Scraping
```powershell
python main.py
```
Program akan secara otomatis:
1. Menjalankan pengujian scraping statis (Requests + BS4) pada 3 halaman.
2. Menjalankan scraping dinamis (Selenium Headless) pada 3 halaman.
3. Menyimpan screenshot halaman 1 ke `output/screenshot_quotes.png`.
4. Mengekstrak data kutipan, penulis, dan tag dari 3 halaman.
5. Menyimpan data ke `output/kutipan.csv` dengan encoding `utf-8-sig`.
6. Mengukur dan menampilkan perbandingan waktu eksekusi serta ringkasan teknis di konsol.

---

## 📊 Hasil Pengujian & Komparasi

| Parameter | Scraping Statis (Requests + BS4) | Scraping Dinamis (Selenium Headless) |
| :--- | :--- | :--- |
| **Pustaka Utama** | `requests`, `beautifulsoup4` | `selenium` (Chrome Headless) |
| **Jumlah Halaman** | 3 Halaman | 3 Halaman |
| **Jumlah Kutipan Terambil**| **0 Kutipan** (Gagal) | **30 Kutipan** (Berhasil Penuh) |
| **Waktu Eksekusi Aktual**  | **~5.43 detik** | **~13.69 detik** |
| **Penyebab Hasil** | Hanya mengunduh raw HTML tanpa engine JavaScript; elemen `.quote` belum dirakit oleh server. | Menjalankan engine JavaScript V8 Chrome dan explicit wait hingga elemen DOM selesai dirender. |

---

## 🔍 Petunjuk Manual Chrome DevTools Network (Analisis XHR)

Untuk membuktikan apakah terdapat endpoint API / XHR terpisah:
1. Buka browser **Google Chrome** di laptop Anda.
2. Buka alamat: [https://quotes.toscrape.com/js/](https://quotes.toscrape.com/js/)
3. Tekan tombol `F12` atau klik kanan pada halaman dan pilih **Inspect** untuk membuka Chrome DevTools.
4. Buka tab **Network** pada panel atas DevTools.
5. Pada baris filter tipe permintaan, klik tombol **Fetch/XHR**.
6. Tekan tombol `Ctrl + R` (atau tombol refresh browser) untuk merekam semua request jaringan.
7. **Hasil Pengamatan:** Daftar permintaan Fetch/XHR tetap **kosong (tidak ada request API)**.
8. **Kesimpulan Teknis:** Data kutipan tidak ditarik via panggilan API asinkronus (AJAX/XHR), melainkan telah ditanamkan oleh pembuat website sebagai variabel inline JavaScript `var data = [...]` di dalam tag `<script>` HTML awal, yang kemudian disuntikkan ke DOM oleh jQuery secara lokal.

---

## 📄 Laporan

Laporan lengkap 1–2 halaman yang memuat metodologi, analisis penyebab kegagalan scraping statis, bukti observasi DevTools Network, dan kesimpulan dapat dibaca langsung pada:
👉 **[laporan_Tugas.md](laporan_Tugas.md)**

---
