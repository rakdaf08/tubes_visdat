import pandas as pd

# 1. Tentukan nama file input dan output
# Ganti dengan path file Excel milikmu yang sebenarnya
input_file = './sources/Middle-east-conflict-data.xlsx' # Pastikan file ini ada di direktori yang sama dengan script ini
output_file = './sources/yemen_conflict_cleaned.csv' # CSV lebih ringan dan optimal untuk Kepler.gl

print("Membaca data Excel...")
df = pd.read_excel(input_file)

# 2. Memfilter data hanya untuk negara Yemen
print("Memfilter area konflik Yemen...")
df_yemen = df[df['COUNTRY'] == 'Yemen'].copy()

# 3. Membersihkan kolom koordinat (Mengganti koma dengan titik)
# Ini wajib agar Kepler.gl mengenali koordinat dengan standar internasional
df_yemen['CENTROID_LATITUDE'] = df_yemen['CENTROID_LATITUDE'].astype(str).str.replace(',', '.').astype(float)
df_yemen['CENTROID_LONGITUDE'] = df_yemen['CENTROID_LONGITUDE'].astype(str).str.replace(',', '.').astype(float)

# 4. Menyimpan data yang sudah bersih ke file CSV baru
df_yemen.to_csv(output_file, index=False)

print(f"✅ Selesai! Data berhasil dibersihkan.")
print(f"Tersisa {len(df_yemen)} titik konflik di Yemen.")
print(f"File siap di-drag and drop ke Kepler: {output_file}")