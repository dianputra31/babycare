# FITUR BACKUP DATABASE

## Overview
Fitur backup database memungkinkan superadmin untuk membackup database (SQLite atau PostgreSQL) dengan progress tracking real-time. Backup berjalan di background thread dan **file otomatis didownload** setelah selesai, dengan dialog "Save As" untuk memilih lokasi penyimpanan.

## Fitur Utama

### 1. **Progress Bar di Header**
- Progress bar ditampilkan di bagian atas halaman (fixed position)
- User bisa navigasi ke halaman lain sambil melihat progress
- Menampilkan persentase backup yang sudah selesai
- Update real-time setiap 1 detik

### 2. **Auto-Download Backup**
- ✅ File backup **otomatis didownload** setelah selesai
- ✅ Browser menampilkan **dialog "Save As"** untuk pilih lokasi
- ✅ User bisa memilih folder tujuan penyimpanan
- ✅ Notifikasi SweetAlert menampilkan nama file

### 3. **Backup Database**
- Support SQLite dan PostgreSQL
- Otomatis compress dengan gzip (file .sql.gz)
- Progress tracking real-time (0-100%)
- Background processing dengan Threading
- Error handling dan logging lengkap

### 4. **Riwayat Backup**
- Halaman daftar backup di `/backup/list/`
- Informasi lengkap: status, progress, ukuran file, tanggal
- Download ulang backup lama jika diperlukan
- Hanya bisa diakses oleh **superadmin**

## Component Files

### 1. Model
**File:** `core/models.py`
```python
class BackupLog(models.Model):
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    progress = models.IntegerField(default=0)  # 0-100%
    file_size = models.BigIntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, ...)
```

### 2. Management Command
**File:** `core/management/commands/backup_database.py`

Command untuk menjalankan backup:
```bash
python manage.py backup_database --backup-id=<id> [--compress]
```

**Fitur:**
- Backup SQLite: Menggunakan `sqlite3.iterdump()`
- Backup PostgreSQL: Menggunakan `pg_dump`
- Update progress secara berkala ke database
- Compress dengan gzip (opsional)

### 3. Views
**File:** `core/views.py`

**Endpoints:**
- `POST /backup/start/` - Mulai backup baru
- `GET /backup/progress/<id>/` - Cek progress backup
- `GET /backup/list/` - Daftar semua backup
- `GET /backup/download/<id>/` - Download file backup

### 4. URLs
**File:** `core/urls.py`

```python
path('backup/start/', views.start_backup, name='start_backup'),
path('backup/progress/<int:backup_id>/', views.backup_progress, name='backup_progress'),
path('backup/list/', views.backup_list, name='backup_list'),
path('backup/download/<int:backup_id>/', views.download_backup, name='download_backup'),
```

### 5. Templates
**File:** `core/templates/core/backup_list.html`
- Halaman daftar backup
- Tombol backup baru
- Tabel riwayat backup dengan status
- Tombol download untuk backup yang selesai

**File:** `core/templates/partials/_navbar.html`
- Tombol backup di navbar (hanya untuk superadmin)
- Progress bar container dengan styling

### 6. JavaScript
**File:** `core/templates/base.html`

**Fungsi utama:**
- `getCookie(name)` - Helper untuk ambil cookie (untuk CSRF token)
- `getCSRFToken()` - Ambil CSRF token dari cookie atau form
- `startBackup()` - Mulai proses backup via AJAX dengan CSRF token
- `startProgressPolling()` - Poll progress setiap 1 detik
- `checkBackupProgress(backupId)` - Update progress bar & auto-download saat selesai
- Auto-download file saat backup completed (trigger browser Save As dialog)
- SweetAlert notification dengan info filename

**CSRF Token Handling:**
- Menggunakan cookie `csrftoken` (Django default)
- Fallback ke hidden form input `csrfmiddlewaretoken`
- Header: `X-CSRFToken` dalam AJAX request
- Credential: `same-origin` untuk security

## Cara Penggunaan

### Untuk Superadmin:

1. **Mulai Backup:**
   - Klik icon database (💾) di navbar
   - Dialog konfirmasi muncul dengan info bahwa file akan auto-download
   - Klik "Mulai Backup"

2. **Monitor Progress:**
   - Progress bar muncul otomatis di bagian atas
   - Tetap bisa navigasi ke halaman lain
   - Progress update otomatis setiap 1 detik
   - Status: "Backup sedang berjalan..." → "Backup selesai! Mengunduh file..."

3. **Pilih Lokasi Penyimpanan:**
   - Setelah backup 100%, browser otomatis trigger download
   - **Dialog "Save As" muncul** dari browser
   - **Pilih folder/lokasi** tempat menyimpan file
   - Klik "Save"
   - File tersimpan dengan nama: `backup_sqlite_YYYYMMDD_HHMMSS.sql.gz`

4. **Download Ulang (Opsional):**
   - Buka `/backup/list/`
   - Cari backup yang diinginkan
   - Klik tombol download 📥
   - Pilih lokasi penyimpanan lagi

## Lokasi File Backup

```
E:\projects\python\django\teguh\babycare\
└── backups/
    ├── backup_sqlite_20260411_123456.sql.gz
    ├── backup_postgres_20260411_134567.sql.gz
    └── ...
```

## Security

- **Hanya superadmin** yang bisa:
  - Melihat tombol backup
  - Memulai backup
  - Melihat riwayat backup
  - Download file backup

- Non-superadmin akan mendapat error 403 (Forbidden)

## Database Support

### SQLite
- Menggunakan `sqlite3.iterdump()`
- Menghasilkan SQL dump lengkap
- Support semua table dan data

### PostgreSQL
- Menggunakan `pg_dump` command
- Memerlukan PostgreSQL client tools
- Environment variable `PGPASSWORD` untuk auth
- Options: `--no-owner --no-acl`

## Error Handling

1. **Backup in progress**: Tidak bisa start backup baru
2. **Database error**: Dicatat di `error_message`
3. **Missing permissions**: 403 Forbidden
4. **File not found**: 404 Not Found
5. **Command failed**: Detail error di `BackupLog.error_message`

## Progress Tracking

Status progress:
- **0-10%**: Inisialisasi
- **10-30%**: Setup connection
- **30-90%**: Dump data (incremental update)
- **90-95%**: Finalisasi
- **95-100%**: Cleanup & save

## Migration

**File:** `core/migrations/0013_add_backup_log.py`

Membuat tabel `backup_log` dengan kolom:
- id, filename, status, progress, file_size
- error_message, started_at, completed_at, created_by

## Future Improvements

1. **Scheduled Backup**: Cron job untuk backup otomatis
2. **Retention Policy**: Auto-delete backup lama
3. **Cloud Storage**: Upload ke S3/Azure/GCS
4. **Restore Functionality**: Restore dari backup
5. **Email Notification**: Notif setelah backup selesai
6. **Backup Encryption**: Encrypt file backup
7. **Incremental Backup**: Hanya backup perubahan

## Testing

### Manual Test:
1. Login sebagai superadmin
2. Klik icon database di navbar
3. Progress bar muncul
4. Tunggu hingga 100%
5. Cek folder `backups/`
6. Download dari halaman backup list

### Command Line Test:
```bash
# Buat backup log entry manual
python manage.py shell
>>> from core.models import BackupLog, User
>>> user = User.objects.first()
>>> backup = BackupLog.objects.create(filename='test', created_by=user)
>>> backup.id

# Run backup command
python manage.py backup_database --backup-id=<ID> --compress
```

## Troubleshooting

### 1. CSRF Token Error (403 Forbidden)
**Error:** `Forbidden (CSRF token from the 'X-Csrftoken' HTTP header has incorrect length.)`

**Solusi:**
- Pastikan JavaScript function `getCSRFToken()` bekerja dengan benar
- Django harus set cookie `csrftoken` - pastikan ada {% csrf_token %} di template
- Clear browser cookies dan refresh halaman
- Cek browser console untuk melihat nilai CSRF token yang dikirim
- Pastikan `credentials: 'same-origin'` ada di fetch request

### 2. File Tidak Auto-Download
**Masalah:** Backup selesai tapi file tidak download otomatis

**Solusi:**
- **Cek Browser Settings:**
  - Chrome: Settings → Downloads → pastikan "Ask where to save each file" aktif
  - Firefox: Settings → General → Downloads → pilih "Always ask where to save files"
  - Edge: Settings → Downloads → aktifkan "Ask me what to do with each download"
- **Pop-up Blocker:** Pastikan browser tidak block download
- **JavaScript Console:** Cek apakah ada error saat trigger download
- Download manual dari halaman `/backup/list/`

### 3. Dialog "Save As" Tidak Muncul
**Masalah:** File langsung download ke folder default

**Solusi:**
- Di browser settings, ubah download behavior menjadi "Always ask"
- Atau cek folder Downloads default browser Anda

### 4. Backup Stuck di Progress Tertentu
**Masalah:** Progress bar berhenti di angka tertentu

**Solusi:**
- Cek log Django console di terminal
- Periksa koneksi database
- Restart Django server
- Cek folder `backups/` di root project

### 5. pg_dump Command Not Found (PostgreSQL)
**Masalah:** Error saat backup PostgreSQL

**Solusi:**
- Install PostgreSQL client tools
- Tambahkan PostgreSQL bin folder ke PATH environment variable
- Restart terminal/cmd setelah update PATH

### 6. Permission Denied Saat Download
**Masalah:** Error 403 saat download

**Solusi:**
- Pastikan login sebagai superadmin
- Cek file ada di folder `backups/`
- Pastikan file permissions di server sudah benar

### 7. Progress Tidak Update
**Masalah:** Progress bar stuck di 0% atau tidak berubah

**Solusi:**
- Cek JavaScript console untuk error
- Pastikan AJAX endpoint `/backup/progress/<id>/` berfungsi
- Clear browser cache
- Refresh halaman dan coba lagi

## Notes

- Backup berjalan di background thread (daemon=True)
- File backup di-compress dengan gzip untuk hemat storage
- Progress polling interval: 1 detik
- Auto-download triggered 0.5 detik setelah backup completed
- Filename format: `backup_{engine}_{timestamp}.sql.gz`
- Browser "Save As" dialog memungkinkan user pilih lokasi penyimpanan

## Browser Download Settings

### Google Chrome
1. Buka Settings (⚙️)
2. Search "Downloads"
3. Aktifkan **"Ask where to save each file before downloading"**
4. Setiap download akan muncul dialog pilih lokasi

### Mozilla Firefox  
1. Buka Settings/Options
2. Pilih tab **General**
3. Di bagian Downloads, pilih **"Always ask you where to save files"**
4. Klik OK

### Microsoft Edge
1. Buka Settings
2. Search "Downloads" 
3. Aktifkan **"Ask me what to do with each download"**
4. Atau set lokasi default di "Downloads location"

### Cara Cepat
- Shortcut keyboard: `Ctrl+J` untuk buka Downloads page
- Klik kanan pada file → "Show in folder" untuk lihat lokasi
- Di browser settings, bisa set default download folder
