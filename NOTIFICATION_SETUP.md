# Sistem Notifikasi Otomatis - Babycare

## Fitur Notifikasi

Sistem notifikasi otomatis akan membuat notifikasi untuk:

1. **🎂 Ulang Tahun Anak** - Setiap hari akan cek apakah ada anak yang ultah hari ini
2. **📋 Jadwal Terapi Hari Ini** - Notifikasi untuk terapi yang dijadwalkan hari ini  
3. **⏰ Besok Terapi** - Pengingat 1 hari sebelum terapi
4. **📅 Reminder 7 Hari** - Pengingat 7 hari sebelum jadwal terapi
5. **⚠️ Pasien Tidak Aktif** - Pasien yang sudah 30 hari tidak kembali

## Cara Menggunakan

### Testing Manual (Command Line)

Untuk testing, jalankan command berikut di terminal:

```bash
# Jalankan langsung (akan create notifikasi ke database)
python manage.py generate_notifications

# Preview saja tanpa create ke database (DRY RUN)
python manage.py generate_notifications --dry-run
```

### Output Example

```
=== Generate Notifications (2025-01-28) ===

Checking birthday notifications...
  ✓ Birthday: Ahmad (2 tahun)
  ✓ Birthday: Siti (5 tahun)

Checking today's therapy schedule...
  ✓ Today: Budi - Terapi Wicara

Checking upcoming therapy notifications (7 days)...
  ✓ Reminder 7 days: Rini - Sensori Integrasi

Checking tomorrow's therapy notifications...
  ✓ Tomorrow: Andi - Terapi Okupasi

Checking 30-day inactive patients...
  ⚠ Inactive: Joko (45 hari)

==================================================

✅ SUMMARY:
  🎂 Birthday notifications: 2
  📋 Today's therapy: 1
  📅 7-day reminders: 1
  ⏰ Tomorrow therapy: 1
  ⚠️  30-day inactive: 1
  📊 TOTAL: 6 notifications

✅ Notifications created successfully!

==================================================
```

## Set Up Jadwal Otomatis

Agar notifikasi generate otomatis setiap hari, gunakan **Windows Task Scheduler**:

### Langkah-langkah:

1. **Buka Task Scheduler**
   - Tekan `Win + R`
   - Ketik `taskschd.msc`
   - Enter

2. **Create New Task**
   - Klik "Create Basic Task..."
   - Nama: `Babycare - Generate Notifications`
   - Description: `Auto-generate daily notifications for birthdays and therapy reminders`
   - Klik Next

3. **Trigger (Jadwal)**
   - Pilih: **Daily**
   - Klik Next
   - Start date: Pilih tanggal mulai (hari ini)
   - Start time: **00:01** (tengah malam lewat 1 menit)
   - Recur every: **1 days**
   - Klik Next

4. **Action**
   - Pilih: **Start a program**
   - Klik Next
   - Program/script: Ketik path Python Anda, contoh:
     ```
     C:\Python311\python.exe
     ```
     atau cari dengan tombol Browse
   
   - Add arguments:
     ```
     manage.py generate_notifications
     ```
   
   - Start in: Ketik path project Anda:
     ```
     e:\projects\python\django\teguh\babycare
     ```
   - Klik Next

5. **Finish**
   - Centang "Open the Properties dialog..."
   - Klik Finish

6. **Properties (Optional Settings)**
   - Tab **General**:
     - Centang "Run whether user is logged on or not"
     - Centang "Run with highest privileges"
   
   - Tab **Conditions**:
     - Uncheck "Start the task only if the computer is on AC power"
   
   - Tab **Settings**:
     - Centang "Run task as soon as possible after a scheduled start is missed"
     - Centang "If the task fails, restart every: 10 minutes"
   
   - Klik OK

### Cara Cari Path Python

Buka Command Prompt dan ketik:

```cmd
where python
```

Atau di PowerShell:

```powershell
Get-Command python | Select-Object -ExpandProperty Source
```

## Monitoring Notifikasi

Setelah command berjalan (manual atau otomatis), cek hasilnya:

1. **Login ke aplikasi Babycare**
2. **Lihat badge notifikasi** di navbar (ikon 🔔)
3. **Klik menu Notifikasi** di sidebar
4. **Filter** berdasarkan:
   - Status: Semua / Belum Dibaca / Sudah Dibaca
   - Jenis: Ulang Tahun, Jadwal Hari Ini, Besok Terapi, dst.

## Troubleshooting

### Command Error

Jika muncul error saat run manual:

```bash
# Pastikan sudah masuk virtual environment dulu
cd e:\projects\python\django\teguh\babycare
venv\Scripts\activate

# Baru run command
python manage.py generate_notifications
```

### Task Scheduler Tidak Jalan

1. **Cek History** di Task Scheduler:
   - Klik kanan pada task → Properties
   - Tab History
   - Lihat error message

2. **Pastikan path benar**:
   - Path Python: `C:\Python311\python.exe`
   - Arguments: `manage.py generate_notifications`
   - Start in: `e:\projects\python\django\teguh\babycare`

3. **Test manual run**:
   - Klik kanan task → Run
   - Lihat hasilnya di History

### Notifikasi Duplikat

Sistem sudah dilengkapi **duplikasi check**:
- Hanya akan create notifikasi jika belum ada untuk kombinasi (pasien, jenis, tanggal) yang sama
- Aman dijalankan berkali-kali

## Tips

1. **Testing pertama** gunakan `--dry-run` untuk preview dulu
2. **Set jadwal** di tengah malam (00:01) supaya tepat waktu
3. **Check log** di terminal untuk monitoring hasil
4. **Mark as read** setelah ditindaklanjuti
5. **Filter by jenis** untuk cari notifikasi tertentu

---

**Dibuat:** 28 Januari 2025  
**Untuk:** Babycare Management System
