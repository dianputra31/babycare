# Dokumentasi Fitur Baru - Pengaturan dan User Management

## Ringkasan Perubahan

Saya telah menambahkan dua fitur baru ke aplikasi Babycare:

### 1. Menu Pengaturan
Menu pengaturan memungkinkan admin untuk mengkonfigurasi aplikasi dengan dua opsi:

#### a. Ukuran Font
- Tersedia slider untuk memilih ukuran font antara 10px hingga 24px
- Preview langsung menampilkan bagaimana teks akan terlihat
- Pengaturan font berlaku secara global di seluruh aplikasi
- Default: 14px

#### b. Upload Logo
- Admin dapat mengupload logo aplikasi
- Logo akan ditampilkan di header (navbar) sebelah tulisan "Babycare"
- Format file: JPG, PNG (max 2MB recommended)
- Preview logo saat ini ditampilkan jika sudah ada

**URL:** `/pengaturan/`

### 2. Sub Menu User di Master Data
Menu untuk mengelola user yang dapat login ke aplikasi:

#### Fitur User Management:
- **List User:** Menampilkan semua user dengan informasi username, nama lengkap, email, cabang, dan status
- **Tambah User:** Form untuk membuat user baru (password wajib diisi)
- **Edit User:** Form untuk mengubah data user (password opsional - kosongkan jika tidak ingin mengubah)
- **Aktif/Non-Aktif:** Toggle status user dengan satu klik (tidak menghapus, hanya menonaktifkan)

**URL:** `/user/`

## File yang Dibuat/Diubah

### Model Baru
- `core/models.py` - Menambahkan model `AppSettings`

### Forms Baru
- `core/forms.py` - Menambahkan:
  - `AppSettingsForm` - Form untuk pengaturan
  - `UserForm` - Form untuk edit user
  - `UserCreateForm` - Form untuk tambah user baru

### Views Baru
- `core/views.py` - Menambahkan:
  - `AppSettingsView` - View untuk pengaturan
  - `UserListView` - List semua user
  - `UserCreateView` - Tambah user baru
  - `UserEditView` - Edit user
  - `UserToggleActiveView` - Aktif/nonaktifkan user

### Templates Baru
- `core/templates/core/pengaturan.html` - Halaman pengaturan
- `core/templates/core/user_list.html` - Daftar user
- `core/templates/core/user_form.html` - Form tambah/edit user

### Template yang Diubah
- `core/templates/partials/_sidebar.html` - Menambahkan menu Pengaturan dan submenu User
- `core/templates/partials/_navbar.html` - Menampilkan logo jika ada
- `core/templates/base.html` - Menerapkan font size dinamis

### Context Processor
- `core/context_processors.py` - Menambahkan `app_settings()` untuk menyediakan font_size dan logo_url ke semua template

### URLs
- `core/urls.py` - Menambahkan routing untuk:
  - `/pengaturan/`
  - `/user/`
  - `/user/new/`
  - `/user/<id>/edit/`
  - `/user/<id>/toggle-active/`

### Settings & URLs Project
- `babycare_project/settings.py` - Menambahkan:
  - Context processor `app_settings`
  - MEDIA_URL dan MEDIA_ROOT untuk upload file
- `babycare_project/urls.py` - Menambahkan static file serving untuk development

### Migrations
- `core/migrations/0002_appsettings.py` - Membuat tabel app_settings
- `core/migrations/0003_add_updated_by_fk.py` - Menambahkan foreign key ke user

## Cara Menggunakan

### Mengatur Font Size dan Logo:
1. Login ke aplikasi
2. Klik menu "Pengaturan" di sidebar
3. Gunakan slider untuk memilih ukuran font
4. Upload logo (opsional)
5. Klik "Simpan Pengaturan"
6. Refresh halaman untuk melihat perubahan

### Mengelola User:
1. Login ke aplikasi
2. Klik menu "Master Data" → "User"
3. **Tambah User Baru:**
   - Klik tombol "Tambah User"
   - Isi form (username, nama lengkap, email, cabang, password)
   - Klik "Simpan"
4. **Edit User:**
   - Klik tombol edit (ikon pensil) pada user yang ingin diubah
   - Ubah data yang diperlukan
   - Kosongkan password jika tidak ingin mengubahnya
   - Klik "Simpan"
5. **Aktif/Nonaktifkan User:**
   - Klik tombol toggle (ikon centang/silang) pada user
   - Konfirmasi aksi

## Catatan Penting

1. **Database:** Fitur ini membuat tabel baru `app_settings` di database
2. **Media Files:** Logo disimpan di folder `media/logos/`
3. **Permissions:** Saat ini semua user yang login dapat mengakses menu ini. Untuk production, sebaiknya ditambahkan permission checks.
4. **Font Size:** Ukuran font diterapkan secara global menggunakan CSS dinamis
5. **Logo:** Logo ditampilkan di navbar jika sudah diupload

## Dependencies Baru
- **Pillow:** Library Python untuk image processing (sudah diinstall)

## Testing
Server sudah berjalan di http://127.0.0.1:8000/

Silakan test fitur-fitur baru dengan:
1. Akses `/pengaturan/` untuk menu Pengaturan
2. Akses `/user/` untuk menu User Management
