import pandas as pd

# 1. Tentukan nama file input dan output
# Ganti dengan path file Excel milikmu yang sebenarnya
input_file = './sources/Middle-east-conflict-data.xlsx' # Pastikan file ini ada di direktori yang sama dengan script ini
output_file = './sources/yemen_conflict_cleaned.csv' # CSV lebih ringan dan optimal untuk Kepler.gl

print("Membaca data Excel...")
df = pd.read_excel(input_file)

print("Memfilter area konflik Yaman...")
df_yemen = df[df['COUNTRY'] == 'Yemen'].copy()

print("Memfilter tanggal mulai Oktober 2023...")
# Konversi kolom WEEK menjadi tipe datetime agar bisa difilter
df_yemen['WEEK'] = pd.to_datetime(df_yemen['WEEK'], format='%d-%B-%Y')
# Ambil hanya kejadian setelah 1 Oktober 2023
df_yemen = df_yemen[df_yemen['WEEK'] >= '2023-10-01']

print("Membersihkan koordinat...")
df_yemen['CENTROID_LATITUDE'] = df_yemen['CENTROID_LATITUDE'].astype(str).str.replace(',', '.').astype(float)
df_yemen['CENTROID_LONGITUDE'] = df_yemen['CENTROID_LONGITUDE'].astype(str).str.replace(',', '.').astype(float)

# Mengubah tanggal kembali ke format string untuk CSV (opsional, agar rapi)
df_yemen['WEEK'] = df_yemen['WEEK'].dt.strftime('%Y-%m-%d')

df_yemen.to_csv(output_file, index=False)

print(f"✅ Selesai! Data berhasil dibersihkan dan difilter.")
print(f"Tersisa {len(df_yemen)} titik serangan maritim Houthi.")