# Perbaikan Form - 16 Feb 2026

## ✅ Yang Sudah Diperbaiki

### 1. **Form Pasien Baru** (`/pasien/new/`)
**Sebelum:** Hanya 3 field (nama_anak, tanggal_lahir, cabang)  
**Sekarang:** 7 field LENGKAP
- ✅ Nama Anak
- ✅ Tanggal Lahir (dengan datepicker)
- ✅ Jenis Kelamin (dropdown: L/P)
- ✅ Nama Orang Tua
- ✅ Alamat (textarea)
- ✅ No WhatsApp
- ✅ Cabang
- ✅ **Kode Pasien** (auto-generate: P0001, P0002, dst)

**File diubah:**
- `core/templates/core/pasien_form.html` - tambah 4 field yang hilang
- `core/views.py` - tambah auto-generate kode_pasien di form_valid()

---

### 2. **Form Pemasukan** (`/pemasukan/new/`)
**Sebelum:** Hanya 4 field (registrasi, jumlah, keterangan, cabang)  
**Sekarang:** 6 field LENGKAP
- ✅ **Tanggal** (BARU - dengan datepicker)
- ✅ Registrasi
- ✅ Jumlah
- ✅ **Metode Pembayaran** (sudah ada di form tapi tidak muncul di template)
- ✅ Cabang
- ✅ Keterangan

**File diubah:**
- `core/forms.py` - tambah field 'tanggal' ke PemasukanForm
- `core/models.py` - ubah Pemasukan.tanggal dari auto_now_add ke editable
- `core/templates/core/pemasukan_form.html` - tambah field tanggal & metode_pembayaran

---

### 3. **Datepicker di Semua Form**
Semua input tanggal sekarang pakai `type="date"` (native browser datepicker):
- ✅ Form Pasien - `tanggal_lahir`
- ✅ Form Registrasi - `tanggal_kunjungan`
- ✅ Form Pemasukan - `tanggal`

Browser modern (Chrome, Edge, Firefox) otomatis menampilkan calendar picker yang responsif.

---

## ✅ Form Lain yang Sudah Lengkap

### 4. **Form Terapis** (`/terapis/new/`)
✅ Sudah LENGKAP - 6 field sesuai database:
- nama_terapis
- no_hp
- alamat
- cabang
- biaya_transport_default
- is_active

### 5. **Form Jenis Terapi** (`/jenis-terapi/new/`)
✅ Sudah LENGKAP - 4 field sesuai database:
- nama_terapi
- kategori_usia_min
- kategori_usia_max
- harga

### 6. **Form Cabang** (`/cabang/new/`)
✅ Sudah LENGKAP - 2 field sesuai database:
- nama_cabang
- alamat

### 7. **Form Registrasi** (`/registrasi/new/`)
✅ Sudah LENGKAP - 9 field sesuai database:
- pasien
- jenis_terapi
- terapis
- tanggal_kunjungan (dengan datepicker)
- harga
- biaya_transport
- cabang
- status (dropdown)
- catatan
- **kode_registrasi** (auto-generate di backend)

---

## 📋 Testing Checklist

Sekarang test semua form:

- [ ] `/pasien/new/` - 7 field tampil semua, simpan berhasil dengan kode P0001
- [ ] `/terapis/new/` - 6 field tampil semua  
- [ ] `/jenis-terapi/new/` - 4 field tampil semua
- [ ] `/cabang/new/` - 2 field tampil semua
- [ ] `/registrasi/new/` - 9 field tampil semua, datepicker berfungsi
- [ ] `/pemasukan/new/` - 6 field tampil semua, termasuk tanggal & metode pembayaran

---

## 🔧 Auto-Generate Codes

1. **Kode Pasien**: Format `P0001`, `P0002`, dst
   - Logic: Ambil ID terakhir + 1, format 4 digit
   - File: `core/views.py` - `PasienCreateView.form_valid()`

2. **Kode Registrasi**: Format `REG-20260216-0001`
   - Logic: Sudah ada di `core/services/registration_service.py`
   - Auto-generate saat create registrasi

---

## ⚠️ Catatan Production

Saat deploy ke PostgreSQL:
- Pastikan kolom `tanggal` di tabel `babycare.pemasukan` bisa NULL atau ada default value
- Test auto-generate kode_pasien dengan sequence PostgreSQL jika perlu
