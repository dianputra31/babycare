# Kolom-Kolom Baru yang Ditambahkan

## ⚠️ PENTING
Ini adalah **DAFTAR KOLOM** yang perlu Anda tambahkan ke database PostgreSQL production Anda jika kolom-kolom ini **BELUM ADA**.

---

## 📋 Kolom yang Ditambahkan

### 1. Tabel: `babycare.pasien`
```sql
ALTER TABLE babycare.pasien 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
```

**Penjelasan:**
- `updated_at` - Timestamp otomatis saat data diupdate
- `is_deleted` - Soft delete flag (untuk soft delete tanpa hapus data fisik)

---

### 2. Tabel: `babycare.jenis_terapi`
```sql
ALTER TABLE babycare.jenis_terapi 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
```

**Penjelasan:**
- `updated_at` - Timestamp otomatis saat data diupdate
- `is_deleted` - Soft delete flag

---

### 3. Tabel: `babycare.terapis`
```sql
ALTER TABLE babycare.terapis 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
```

**Penjelasan:**
- `updated_at` - Timestamp otomatis saat data diupdate
- `is_deleted` - Soft delete flag

---

### 4. Tabel: `babycare.registrasi`
```sql
ALTER TABLE babycare.registrasi 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE;
```

**Penjelasan:**
- `updated_at` - Timestamp otomatis saat data diupdate
- `is_deleted` - Soft delete flag

---

## 🔍 Cek Kolom yang Sudah Ada

Sebelum menambahkan kolom, cek dulu kolom mana yang sudah ada:

```sql
-- Cek kolom di tabel pasien
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'babycare' 
AND table_name = 'pasien'
AND column_name IN ('updated_at', 'is_deleted');

-- Cek kolom di tabel jenis_terapi
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'babycare' 
AND table_name = 'jenis_terapi'
AND column_name IN ('updated_at', 'is_deleted');

-- Cek kolom di tabel terapis
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'babycare' 
AND table_name = 'terapis'
AND column_name IN ('updated_at', 'is_deleted');

-- Cek kolom di tabel registrasi
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_schema = 'babycare' 
AND table_name = 'registrasi'
AND column_name IN ('updated_at', 'is_deleted');
```

---

## ✅ Hasil Pengecekan dari babycare.sql

Berdasarkan file `db/babycare.sql` yang Anda berikan, kolom-kolom ini **SUDAH ADA** di tabel berikut:

- ✓ `pasien.updated_at` - **SUDAH ADA**
- ✓ `pasien.is_deleted` - **SUDAH ADA**
- ✓ `jenis_terapi.updated_at` - **SUDAH ADA**
- ✓ `jenis_terapi.is_deleted` - **SUDAH ADA**
- ✓ `terapis.updated_at` - **SUDAH ADA** (line 307 di babycare.sql)
- ✓ `terapis.is_deleted` - **SUDAH ADA** (line 308 di babycare.sql)
- ✓ `registrasi.updated_at` - **SUDAH ADA** (line 358 di babycare.sql)
- ✓ `registrasi.is_deleted` - **SUDAH ADA** (line 359 di babycare.sql)

---

## 🎯 Kesimpulan

**TIDAK PERLU MENAMBAHKAN KOLOM APAPUN** ke database PostgreSQL Anda!

Semua kolom yang dibutuhkan oleh Django models **SUDAH ADA** di database PostgreSQL Anda (berdasarkan file `babycare.sql`).

Yang saya lakukan hanya:
1. ✅ Update Django models untuk menggunakan kolom yang sudah ada
2. ✅ Update SQLite development database agar sama dengan PostgreSQL
3. ✅ Fix nama field di middleware (dari `code` ke `nama_role`)

---

## 📝 Catatan Penting

### Jika Anda switch dari SQLite ke PostgreSQL:

1. **Update .env file:**
```env
USE_POSTGRES=True
DB_NAME=babycare_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

2. **Cek satu lagi - nama kolom cabang di users:**
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'babycare' 
AND table_name = 'users'
AND column_name LIKE '%cabang%';
```

Jika hasilnya `cabang_id`, update [core/models.py](../core/models.py) line 85:
```python
# Dari:
cabang = models.ForeignKey(Cabang, db_column='cabang', ...)

# Ke:
cabang = models.ForeignKey(Cabang, db_column='cabang_id', ...)
```

3. **Test koneksi:**
```bash
python manage.py check
python manage.py showmigrations
```

---

## 📞 Support

Jika ada pertanyaan atau error saat deploy ke PostgreSQL, silakan tanyakan!

**Last Updated**: February 16, 2026
