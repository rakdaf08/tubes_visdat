import pandas as pd

# 1. Tentukan nama file input dan output
# Ganti dengan path file Excel milikmu yang sebenarnya
input_file = './sources/Middle-east-conflict-data.xlsx' # Pastikan file ini ada di direktori yang sama dengan script ini
output_file = './sources/yemen_conflict_cleaned.csv' # CSV lebih ringan dan optimal untuk Kepler.gl

print("Membaca data Excel ACLED...")
df = pd.read_excel(input_file)
print(f"Total data awal: {len(df)} baris.")

# 2. Filter 1: Hanya wilayah Yemen
df = df[df['COUNTRY'] == 'Yemen'].copy()

# 3. Filter 2: Tanggal mulai 1 Oktober 2023
# Konversi teks ke datetime agar bisa difilter
df['WEEK'] = pd.to_datetime(df['WEEK'], format='%d-%B-%Y')
df = df[df['WEEK'] >= '2023-10-01']

# 4. Filter 3: Sub-Event Type yang relevan dengan serangan kapal/maritim
target_events = [
    'Air/drone strike', 
    'Shelling/artillery/missile attack', 
    'Attack', 
    'Abduction/forced disappearance',
    'Armed clash'
]
df = df[df['SUB_EVENT_TYPE'].isin(target_events)]

# 5. Pembersihan Koordinat (Ubah koma jadi titik)
# Ini krusial agar Kepler.gl mengenali lokasi dengan tepat
df['CENTROID_LATITUDE'] = df['CENTROID_LATITUDE'].astype(str).str.replace(',', '.').astype(float)
df['CENTROID_LONGITUDE'] = df['CENTROID_LONGITUDE'].astype(str).str.replace(',', '.').astype(float)

# Mengembalikan format tanggal menjadi string agar rapi di CSV
df['WEEK'] = df['WEEK'].dt.strftime('%Y-%m-%d')

# 6. Simpan hasil akhir
df.to_csv(output_file, index=False)

print("\n✅ Eksekusi Selesai!")
print(f"Tersisa {len(df)} titik konflik maritim yang sangat relevan.")
print(f"File siap dimasukkan ke Kepler.gl: {output_file}")