# 🌊 Red Sea Crisis: Houthi Conflict & Maritime Trade Impact

Dashboard Analitis Interaktif yang dibangun menggunakan **Streamlit** untuk memvisualisasikan data konflik Houthi di Timur Tengah (khususnya Yaman) dan dampaknya terhadap lalu lintas pelayaran global di Selat Bab-Al Mandab, Terusan Suez, dan rute alternatif Tanjung Harapan (Cape of Good Hope).

---

## 📌 Identifikasi & Deskripsi Aplikasi (`main.py`)

Aplikasi utama dijalankan melalui berkas `main.py`. Dashboard ini memiliki beberapa fitur utama:
1. **Regional Conflict Overview (Tab 1)**: Visualisasi persebaran dan intensitas konflik di Timur Tengah berdasarkan negara, visualisasi spasial menggunakan peta interaktif Maplibre yang di-overlay dengan rute pelayaran laut utama (*shipping lanes*), serta tren konflik bulanan.
2. **Yemen & Houthi Deep-Dive (Tab 2)**: Analisis mendalam tipe serangan (misal: serangan drone, rudal, bentrokan bersenjata), timeline bulanan kejadian dan korban jiwa di Yaman, serta visualisasi Word Cloud dari tipe sub-kejadian (*sub-event type*).
3. **Maritime Impact (Tab 3)**: Grafik lalu lintas mingguan kapal di berbagai selat/terusan utama, perbandingan pangsa lalu lintas sebelum dan sesudah krisis (*Pre-Crisis* vs *Post-Crisis*), serta grafik korelasi antara intensitas konflik di Yaman dengan rata-rata penyeberangan mingguan di Terusan Suez.

---

## 📂 Struktur Data yang Dibutuhkan

Aplikasi secara otomatis mendeteksi berkas data di direktori utama atau di dalam folder `sources/`. Pastikan berkas-berkas berikut tersedia di dalam folder [sources/](file:///C:/Users/rakad/OneDrive/Dokumen/ITB/Spesialisasi/Visdat/tubes_visdat/sources/):

1. **Data Konflik**:
   * Lokasi: `sources/Middle-east-conflict-data.xlsx`
   * Deskripsi: Berisi data mingguan kejadian konflik, jumlah kejadian, korban jiwa, serta koordinat geografis (latitude & longitude) negara-negara di Timur Tengah.
2. **Data Pelayaran Kapal**:
   * Lokasi: `sources/upload-weeklyshipcrossingsforsixmaritimepassagesofinterest.csv`
   * Deskripsi: Data mingguan jumlah penyeberangan kapal (*number of crossings*) untuk beberapa selat penting seperti Terusan Suez, Selat Bab-Al Mandab, dan Tanjung Harapan.
3. **Peta Rute Pelayaran (GeoJSON)**:
   * Lokasi: `sources/shipping_lanes/Shipping_Lanes_v1.geojson`
   * Deskripsi: Data spasial koordinat jalur pelayaran utama dunia untuk di-overlay di atas peta interaktif.

---

## 🛠️ Persyaratan Sistem & Instalasi (`requirements.txt`)

Berkas dependencies telah didefinisikan di dalam [requirements.txt](file:///C:/Users/rakad/OneDrive/Dokumen/ITB/Spesialisasi/Visdat/tubes_visdat/requirements.txt):
```text
streamlit>=1.30.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
matplotlib>=3.7.0
wordcloud>=1.9.0
openpyxl>=3.1.0
```

### Opsi 1: Instalasi Menggunakan Virtual Environment Standar (Pip)

1. Buat virtual environment (opsional namun sangat disarankan):
   ```bash
   python -m venv .venv
   ```
2. Aktifkan virtual environment:
   * **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   * **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
3. Instal seluruh dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Opsi 2: Instalasi Menggunakan `uv` (Lebih Cepat & Modern)

Karena repositori ini sudah memiliki konfigurasi `pyproject.toml` dan `uv.lock`, Anda dapat menggunakan [uv](https://github.com/astral-sh/uv) untuk manajemen virtual environment yang jauh lebih cepat:
```bash
# Membuat virtual environment dan menginstal dependensi otomatis
uv sync
```

---

## 🚀 Cara Menjalankan Aplikasi

Setelah semua dependensi terinstal dan virtual environment aktif, jalankan perintah berikut dari direktori utama proyek:

```bash
streamlit run main.py
```

Setelah dijalankan, terminal akan menampilkan alamat URL lokal (biasanya `http://localhost:8501`). Buka alamat tersebut pada peramban (browser) Anda untuk melihat dashboard.

---

## 🖥️ Teknologi yang Digunakan
* **Bahasa**: Python 3.13+
* **Framework Dashboard**: Streamlit
* **Analisis Data**: Pandas, NumPy
* **Visualisasi Grafis**: Plotly (Express & Graph Objects), Matplotlib, WordCloud
* **Pembaca Excel**: Openpyxl
