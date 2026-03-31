# Panduan Instalasi Babycare di Windows 8.1

Dokumen ini ditujukan untuk instalasi lokal aplikasi Babycare pada Windows 8.1 64-bit.

Catatan penting:

- Windows 8.1 masih mungkin dipakai untuk aplikasi ini, tetapi tidak direkomendasikan untuk instalasi baru jangka panjang.
- Windows 8.0 tidak disarankan.
- Untuk hasil paling stabil, gunakan PostgreSQL 13 dan Python 3.10 atau 3.11 64-bit.

## 1. Kebutuhan Sistem

Minimum yang disarankan:

- Windows 8.1 64-bit
- RAM 4 GB minimum, 8 GB lebih aman
- Ruang kosong 5-10 GB
- Koneksi internet untuk instalasi dependency

Software yang perlu diinstall:

- Microsoft Visual C++ Redistributable 2015-2022 x64
- Python 3.10 atau Python 3.11 64-bit
- PostgreSQL 13
- Git
- Browser modern seperti Google Chrome

## 2. Siapkan Folder Project

Contoh lokasi project:

```powershell
D:\apps\babycare
```

Jika project didapat dari Git:

```powershell
git clone <url-repository> D:\apps\babycare
cd D:\apps\babycare
```

Jika project sudah berupa folder copy, cukup pastikan semua file project sudah berada dalam satu folder yang lengkap.

## 3. Buat Virtual Environment Python

Buka PowerShell di folder project, lalu jalankan:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Jika `py -3.11` tidak ada, coba gunakan Python 3.10:

```powershell
py -3.10 -m venv .venv
```

Dependency utama project ini berasal dari [requirements.txt](requirements.txt):

- Django
- psycopg2-binary
- python-dotenv
- openpyxl
- reportlab
- requests
- Pillow

## 4. Siapkan PostgreSQL 13

Setelah PostgreSQL 13 terinstall:

1. Buat database bernama `babycare_db`
2. Pastikan user PostgreSQL Anda punya akses ke database tersebut
3. Import schema dan data awal dari [db/babycare.sql](db/babycare.sql)

Contoh import dengan `psql`:

```powershell
psql -U postgres -d babycare_db -f db\babycare.sql
```

Catatan:

- Project ini menggunakan PostgreSQL dengan `search_path` ke schema `babycare`
- Konfigurasi database dapat dilihat di [babycare_project/settings.py](babycare_project/settings.py)

## 5. Siapkan File .env

Copy file [.env.example](.env.example) menjadi `.env`.

Contoh:

```powershell
Copy-Item .env.example .env
```

Lalu edit isi `.env` sesuai komputer target.

Contoh isi yang aman:

```env
DEBUG=False
SECRET_KEY=ganti-dengan-secret-key-random-yang-panjang

USE_POSTGRES=True
DB_NAME=babycare_db
DB_USER=postgres
DB_PASSWORD=ganti-dengan-password-postgres
DB_HOST=localhost
DB_PORT=5432

FONNTE_API_KEY=
```

Jika ingin memakai SQLite lokal untuk testing cepat:

```env
DEBUG=True
SECRET_KEY=ganti-dengan-secret-key-random-yang-panjang
USE_POSTGRES=False
FONNTE_API_KEY=
```

## 6. Validasi Instalasi

Masih dari PowerShell di folder project:

```powershell
.venv\Scripts\activate
python manage.py check
```

Jika tidak ada error, lanjut jalankan server:

```powershell
python manage.py runserver 0.0.0.0:8000
```

Lalu buka browser:

```text
http://127.0.0.1:8000
```

## 7. Akses dari Komputer Lain dalam LAN

Jika aplikasi mau diakses dari komputer lain dalam jaringan yang sama:

1. Jalankan server dengan:

```powershell
python manage.py runserver 0.0.0.0:8000
```

2. Cek IP lokal komputer server:

```powershell
ipconfig
```

3. Buka dari komputer lain:

```text
http://IP_SERVER:8000
```

Contoh:

```text
http://192.168.1.10:8000
```

4. Pastikan Windows Firewall mengizinkan akses ke port `8000`

## 8. Troubleshooting Singkat

### Python tidak dikenali

Gunakan path penuh Python atau install ulang Python dengan opsi `Add Python to PATH`.

### Gagal install psycopg2-binary atau reportlab

Pastikan `Microsoft Visual C++ Redistributable 2015-2022 x64` sudah terinstall.

### Gagal konek PostgreSQL

Periksa kembali:

- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- service PostgreSQL berjalan

### `manage.py check` gagal

Pastikan virtualenv aktif dan semua package sudah terinstall:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py check
```

## 9. Rekomendasi Operasional

Untuk penggunaan harian di LAN lokal:

- gunakan PostgreSQL, bukan SQLite
- lakukan backup database rutin
- gunakan browser modern
- jika ingin lebih stabil daripada `runserver`, pertimbangkan `waitress`

Contoh menjalankan dengan `waitress`:

```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 babycare_project.wsgi:application
```

## 10. File Referensi Penting

- [babycare_project/settings.py](babycare_project/settings.py)
- [requirements.txt](requirements.txt)
- [db/babycare.sql](db/babycare.sql)
- [.env.example](.env.example)
- [NOTIFICATION_SETUP.md](NOTIFICATION_SETUP.md)