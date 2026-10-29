# LAPORAN PRAKTIKUM
## EKSTRAKSI DAN PENGOLAHAN DATA WEB
### Komparasi Web Scraping Statis vs Dinamis pada Website Berbasis JavaScript (Client-Side Rendering)

---

| Informasi Praktikum | Keterangan |
| :--- | :--- |
| **Mata Kuliah** | Ekstraksi dan Pengolahan Data Web |
| **Target Website** | [https://quotes.toscrape.com/js/](https://quotes.toscrape.com/js/) |
| **Lingkungan Pengujian** | Windows 11, Python 3.13.7, Google Chrome 64-bit |
| **Library Utama** | Requests, BeautifulSoup4, Selenium WebDriver, Pandas |
| **Tanggal Pengujian** | 30 Oktober 2026 |

---

### 1. Pendahuluan & Latar Belakang
Dalam rekayasa data web, arsitektur penyajian konten sebuah website terbagi menjadi dua paradigma utama:
1. **Server-Side Rendering (SSR):** Konten HTML dirakit langsung di server dan dikirim dalam kondisi utuh ke peramban.
2. **Client-Side Rendering (CSR):** Server hanya mengirimkan dokumen HTML kerangka (skeleton) bersama berkas JavaScript. Konten aktual baru dirakit dan disuntikkan ke dalam DOM (*Document Object Model*) oleh JavaScript engine peramban setelah berkas dimuat di sisi klien.

Website `https://quotes.toscrape.com/js/` merupakan representasi website berbasis **Client-Side Rendering**. Praktikum ini bertujuan untuk mengevaluasi efektivitas serta komparasi kinerja antara metode scraping statis (*Requests + BeautifulSoup*) dan dinamis (*Selenium WebDriver with Explicit Wait*).

---

### 2. Metodologi Penelitian & Implementasi

#### A. Metode Statis (Requests + BeautifulSoup4)
1. Skrip mengirimkan permintaan HTTP `GET` ke URL target (`page/1/` hingga `page/3/`).
2. Menerima muatan respons berupa teks dokumen HTML mentah (*raw HTML response*).
3. Melakukan parsing dokumen menggunakan parser `html.parser` dari BeautifulSoup.
4. Menelusuri elemen penampung kutipan dengan selector CSS `div.quote`.

#### B. Metode Dinamis (Selenium WebDriver Headless)
1. Menginisialisasi peramban Google Chrome lokal menggunakan mode *Headless* (`--headless=new`, `--disable-gpu`, `--no-sandbox`) dengan resolusi 1920x1080. Driver dikelola secara otomatis menggunakan Selenium Manager bawaan Selenium 4.52.
2. Membuka URL target halaman 1, 2, dan 3.
3. Menerapkan mekanisme **Explicit Wait** (`WebDriverWait` dikombinasikan dengan `expected_conditions.presence_of_all_elements_located`) selama maksimal 15 detik. Mekanisme ini memastikan skrip menunggu sampai elemen target benar-benar telah dirender oleh mesin JavaScript sebelum proses ekstraksi dimulai.
4. Mengambil tangkapan layar (*screenshot*) pada halaman 1 sebagai bukti visual rendering DOM.
5. Mengekstrak 4 atribut data: `halaman`, `kutipan`, `penulis`, dan `tag`.
6. Menutup sesi peramban (`driver.quit()`) dan menyimpan data ke format CSV berstandar UTF-8 dengan BOM (`utf-8-sig`).

---

### 3. Hasil Pengujian Aktual

Pengujian dijalankan pada 3 halaman pagination web (`/js/page/1/`, `/js/page/2/`, dan `/js/page/3/`). Hasil aktual yang tercatat di terminal adalah sebagai berikut:

| Parameter Pengujian | Metode Statis (Requests + BS4) | Metode Dinamis (Selenium Headless) |
| :--- | :--- | :--- |
| **Status HTTP** | `200 OK` (Semua halaman) | `200 OK` (Tergambar di DOM) |
| **Jumlah Halaman Diproses** | 3 Halaman | 3 Halaman |
| **Total Kutipan Tereksitasi** | **0 Kutipan** (Gagal) | **30 Kutipan** (Berhasil penuh) |
| **Waktu Eksekusi Aktual** | **5.4365 detik** | **13.6900 detik** |
| **Output Berkas Dihasilkan** | Tidak ada data baru | `kutipan.csv` & `screenshot_quotes.png` |

#### Sampel Data Hasil Ekstraksi (5 Baris Pertama)
Data disimpan di `output/kutipan.csv` sebanyak 30 baris data lengkap:
1. **Hal 1 | Albert Einstein**: *"The world as we have created it is a process of our thinking. It cannot be changed without changing our thinking."* (Tags: change, deep-thoughts, thinking, world)
2. **Hal 1 | J.K. Rowling**: *"It is our choices, Harry, that show what we truly are, far more than our abilities."* (Tags: abilities, choices)
3. **Hal 1 | Albert Einstein**: *"There are only two ways to live your life. One is as though nothing is a miracle. The other is as though everything is a miracle."* (Tags: inspirational, life, live, miracle, miracles)
4. **Hal 1 | Jane Austen**: *"The person, be it gentleman or lady, who has not pleasure in a good novel, must be intolerably stupid."* (Tags: aliteracy, books, classic, humor)
5. **Hal 1 | Marilyn Monroe**: *"Imperfection is beauty, madness is genius and it's better to be absolutely ridiculous than absolutely boring."* (Tags: be-yourself, inspirational)

---

### 4. Analisis Teknis & Pembahasan

#### A. Penyebab Kegagalan Metode Statis
Meskipun server merespons dengan kode status `200 OK`, metode scraping statis menghasilkan **0 elemen kutipan**. 

Penyebab kegagalan ini dapat ditinjau langsung dari kode sumber HTML mentah:
```html
<!-- Cuplikan dari respon mentah Requests pada https://quotes.toscrape.com/js/ -->
<div class="row">
    <div class="col-md-8">
        <!-- Container ini KOSONG saat dikirim oleh server! -->
    </div>
</div>
<script src="/static/jquery.js"></script>
<script>
    var data = [
        {"tags": ["change", ...], "author": {"name": "Albert Einstein", ...}, "text": "\u201cThe world..."},
        ...
    ];
    for (var i in data) {
        // jQuery secara dinamis menyusun elemen div class="quote" dan menyuntikkannya ke DOM
    }
</script>
```
Library `requests` hanya berperan sebagai klien HTTP yang mengunduh muatan statis jaringan, sedangkan `BeautifulSoup` hanya mem-parsing pohon tag teks yang sudah ada. Karena `requests` **tidak memiliki mesin JavaScript (JavaScript V8 Engine)**, skrip inline jQuery di atas tidak pernah dieksekusi. Akibatnya, container DOM tetap berstatus kosong dan selector `div.quote` tidak menemukan elemen apapun.

#### B. Analisis Chrome DevTools Network (Pemeriksaan Endpoint XHR/Fetch)
Berdasarkan investigasi jaringan menggunakan DevTools:
1. **Petunjuk Pemeriksaan Manual di Chrome:**
   - Buka browser Google Chrome dan navigasikan ke `https://quotes.toscrape.com/js/`.
   - Tekan tombol `F12` atau klik kanan di mana saja lalu pilih **Inspect**.
   - Klik tab **Network**.
   - Pada bilah filter jenis request, pilih tombol **Fetch/XHR**.
   - Tekan `Ctrl + R` (atau `F5`) untuk memuat ulang halaman sembari merekam aktivitas jaringan.
2. **Temuan Aktual:**
   - Pada filter **Fetch/XHR**, **tidak ditemukan permintaan jaringan sama sekali (daftar kosong)**.
   - Tidak ada endpoint API (seperti REST JSON endpoint) yang dipanggil secara asinkronus oleh browser.
   - **Kesimpulan Sumber Data:** Pengembang website meletakkan data kutipan langsung (*embedded data*) di dalam variabel JavaScript lokal `var data = [...]` di dalam tag `<script>` dokumen HTML utama, lalu menggunakan jQuery untuk memanipulasi DOM. Oleh karena itu, kita tidak dapat mengambil data langsung melalui endpoint XHR terpisah.

#### C. Analisis Komparasi Waktu Eksekusi
- **Metode Statis (5.4365 detik):**
  Hanya membutuhkan waktu latensi jaringan transmisi paket HTTP GET untuk 3 halaman. Proses parsing HTML mentah oleh CPU hanya memerlukan waktu beberapa milidetik.
- **Metode Dinamis (13.6900 detik):**
  Waktu eksekusi sekitar 2.5 kali lebih lambat dibanding metode statis. Hal ini merupakan konsekuensi wajar (*overhead*) dari:
  1. *Spawning* proses binary aplikasi Google Chrome di memori sistem operasi.
  2. Alokasi thread WebDriver dan komunikasi protokol Chrome DevTools Protocol (CDP).
  3. Mengunduh aset eksternal (termasuk berkas `/static/jquery.js`).
  4. Eksekusi runtime JavaScript oleh mesin V8 hingga *event listener* selesai.
  5. Mekanisme *Explicit Wait* yang melakukan *polling* berkala ke DOM hingga elemen siap.

---

### 5. Kesimpulan
1. **Metode Statis (Requests + BeautifulSoup)** sangat efisien dan cepat, namun **tidak dapat digunakan** pada website yang menerapkan Client-Side Rendering murni tanpa rendering awal di sisi server.
2. **Metode Dinamis (Selenium WebDriver)** terbukti **berhasil 100%** mengekstrak seluruh 30 kutipan dari 3 halaman berkat kemampuannya menjalankan runtime peramban utuh dan mengeksekusi skrip JavaScript client-side.
3. Penerapan **Explicit Wait** (`WebDriverWait`) terbukti andal dalam mengatasi *race condition* (kondisi di mana script mencoba mengekstrak data sebelum perakitan DOM oleh JavaScript selesai).
4. Hasil inspeksi **Chrome DevTools Network** membuktikan bahwa website target tidak memanfaatkan pemanggilan API XHR/Fetch eksternal, melainkan menanamkan data langsung pada blok skrip inline HTML.
5. Untuk kebutuhan rekayasa data produksi, Selenium Headless memberikan keandalan ekstraksi tertinggi untuk website dinamis dengan kompromi beban waktu komputasi yang sedikit lebih tinggi.
