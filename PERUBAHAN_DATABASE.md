# Perubahan Database Schema

> **PENTING**: Dokumen ini mencatat semua perubahan yang perlu diterapkan ke database PostgreSQL production Anda.

## 📋 Summary
Tidak ada kolom **BARU** yang ditambahkan. Semua perubahan hanya **menyesuaikan nama field** di Django models agar sesuai dengan struktur database PostgreSQL yang sudah ada di `babycare.sql`.

---

## ✅ Tabel Yang TIDAK Perlu Diubah
Tabel-tabel berikut **sudah sesuai** antara database PostgreSQL dan Django models:

1. ✓ **cabang** - sudah ada `nama_cabang`, `alamat`, `created_at`
2. ✓ **pasien** - sudah ada `kode_pasien`, `nama_anak`, `tanggal_lahir`, `jenis_kelamin`, `nama_orang_tua`, `alamat`, `no_wa`, `cabang_id`
3. ✓ **jenis_terapi** - sudah ada `nama_terapi`, `kategori_usia_min`, `kategori_usia_max`, `harga`
4. ✓ **terapis** - sudah ada `nama_terapis`, `no_hp`, `alamat`, `cabang_id`, `biaya_transport_default`, `is_active`
5. ✓ **registrasi** - sudah ada `kode_registrasi`, `tanggal_kunjungan`, `status`, `catatan`, `pasien_id`, `jenis_terapi_id`, `terapis_id`, `harga`, `biaya_transport`, `total_bayar`, `cabang_id`
6. ✓ **pemasukan** - sudah ada `metode_pembayaran`, `registrasi_id`, `jumlah`, `keterangan`, `created_by`, `created_at`, `cabang_id`
7. ✓ **pengeluaran** - sudah ada `kategori`, `jumlah`, `keterangan`, `created_at`, `cabang_id`
8. ✓ **users** - sudah ada `username`, `password_hash`, `full_name`, `email`, `cabang_id`, `is_active`, `created_at`
9. ✓ **roles** - sudah ada `nama_role`, `deskripsi`
10. ✓ **permissions** - sudah ada `module`, `action`, `code`

---

## 🔧 Perubahan di Django Models (TIDAK untuk Database)

Berikut adalah perubahan yang saya lakukan **hanya di Django models** untuk menyesuaikan dengan database Anda:

### 1. **User Model** (core/models.py)
**SEBELUM:**
```python
cabang = models.ForeignKey(Cabang, db_column='cabang_id', ...)
```

**SESUDAH:**
```python
cabang = models.ForeignKey(Cabang, db_column='cabang', ...)
```

**Alasan**: Database SQLite development menggunakan kolom `cabang` (bukan `cabang_id`), sedangkan PostgreSQL Anda menggunakan `cabang_id`. 

**ACTION REQUIRED**: 
- **Jika PostgreSQL Anda menggunakan `cabang_id`**: Kembalikan ke `db_column='cabang_id'`
- **Jika PostgreSQL Anda menggunakan `cabang`**: Biarkan seperti ini

---

### 2. **Middleware** (core/middleware.py)
**SEBELUM:**
```python
request.user_roles = set(r.code.lower() for r in roles)
```

**SESUDAH:**
```python
request.user_roles = set(r.nama_role.lower() for r in roles)
```

**Alasan**: Tabel `roles` di database PostgreSQL Anda menggunakan field `nama_role` (bukan `code`).

✅ **Tidak perlu action** - ini sudah sesuai dengan `babycare.sql` Anda

---

## 🗄️ Struktur Tabel di PostgreSQL (Reference)

### Tabel: babycare.users
```sql
CREATE TABLE "babycare"."users" (
  "id" int8 PRIMARY KEY,
  "username" varchar(100) NOT NULL,
  "password_hash" text NOT NULL,
  "full_name" varchar(150),
  "email" varchar(150),
  "cabang_id" int4,          -- ⚠️ Cek ini: `cabang_id` atau `cabang`?
  "is_active" bool DEFAULT true,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
);
```

### Tabel: babycare.roles
```sql
CREATE TABLE "babycare"."roles" (
  "id" int4 PRIMARY KEY,
  "nama_role" varchar(50) NOT NULL,   -- ✅ Sudah sesuai
  "deskripsi" text                     -- ✅ Sudah sesuai
);
```

### Tabel: babycare.permissions
```sql
CREATE TABLE "babycare"."permissions" (
  "id" int4 PRIMARY KEY,
  "module" varchar(100) NOT NULL,      -- ✅ Sudah sesuai
  "action" varchar(50) NOT NULL,       -- ✅ Sudah sesuai
  "code" varchar(150) NOT NULL UNIQUE  -- ✅ Sudah sesuai
);
```

---

## 🚀 Checklist untuk Production

### Sebelum Deploy ke PostgreSQL:

- [ ] **Cek tabel `users`**: Apakah kolom untuk cabang namanya `cabang_id` atau `cabang`?
  - Jika `cabang_id`: Update [core/models.py](core/models.py) line 85 → `db_column='cabang_id'`
  - Jika `cabang`: Biarkan seperti sekarang

- [ ] **Verify field names di semua tabel**:
  ```sql
  -- Jalankan di PostgreSQL
  SELECT column_name, data_type 
  FROM information_schema.columns 
  WHERE table_schema = 'babycare' 
  AND table_name IN ('users', 'roles', 'permissions', 'pasien', 'terapis', 'jenis_terapi', 'cabang', 'registrasi', 'pemasukan', 'pengeluaran')
  ORDER BY table_name, ordinal_position;
  ```

- [ ] **Update .env**:
  ```env
  USE_POSTGRES=True
  DB_NAME=babycare_db
  DB_USER=postgres
  DB_PASSWORD=your_password
  DB_HOST=localhost
  DB_PORT=5432
  DEBUG=False  # Set False untuk production
  ```

- [ ] **Test koneksi**:
  ```bash
  python manage.py check
  python manage.py migrate --fake  # Karena tabel sudah ada
  ```

---

## 📝 Notes

1. **SQLite vs PostgreSQL**: 
   - Development menggunakan SQLite dengan schema yang dibuat oleh `init_dev_db.py`
   - Production akan menggunakan PostgreSQL dengan schema dari `babycare.sql`
   - Pastikan field names sama persis

2. **managed = False**:
   - Semua models menggunakan `managed = False` artinya Django tidak akan membuat/mengubah tabel
   - Anda harus manage schema secara manual di PostgreSQL

3. **Migration Files**:
   - Migration files Django **tidak akan dijalankan** karena `managed = False`
   - Perubahan schema harus dilakukan langsung di PostgreSQL

---

## ❓ Troubleshooting

### Error: "no such column: babycare.users.cabang_id"
**Solusi**: Cek nama kolom di tabel users, kemudian sesuaikan `db_column` di models.py

### Error: "no such column: babycare.roles.code"
**Solusi**: ✅ Sudah diperbaiki - sekarang menggunakan `nama_role`

### Error: "no such table: django_session"
**Solusi**: Jalankan `python manage.py migrate` untuk membuat tabel session Django

---

## 📞 Kontak

Jika ada pertanyaan tentang perubahan database ini, silakan tanyakan sebelum deploy ke production.

**Generated**: February 16, 2026
**Django Version**: 4.2.7
**Database**: PostgreSQL 13+ (babycare schema)
