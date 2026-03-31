# Implementasi Sistem Registrasi Multi-Terapi - Langkah Lengkap

## 📋 Ringkasan

Sistem ini memungkinkan satu registrasi pasien memiliki **multiple terapi** sekaligus, bukan hanya 1 terapi. Table `registrasi` menyimpan header transaksi, dan table `registrasi_detail` menyimpan detail setiap terapi.

## ✅ Yang Sudah Selesai

1. **Model `RegistrasiDetail`** sudah dibuat di [core/models.py](core/models.py)
2. **Migration file** sudah dibuat di [core/migrations/0005_registrasidetail.py](core/migrations/0005_registrasidetail.py)
3. **File contoh** sudah dibuat:
   - `CONTOH_FORMS_MULTI_TERAPI.py` - Form dan FormSet
   - `CONTOH_VIEWS_MULTI_TERAPI.py` - Views untuk Create/Edit
   - `CONTOH_TEMPLATE_REGISTRASI_FORM_MULTI.html` - Template HTML
   - `CONTOH_MIGRATION_COMMAND.py` - Command untuk migrasi data lama
   - `CONTOH_UPDATE_LIST_VIEW.html` - Update untuk list view
   - `CONTOH_URLS.py` - Konfigurasi URL

## 📝 Langkah Implementasi

### 1. Run Migration (Database)

```powershell
python manage.py makemigrations
python manage.py migrate
```

### 2. Update Forms (`core/forms.py`)

Copy kode dari `CONTOH_FORMS_MULTI_TERAPI.py` dan tambahkan ke `core/forms.py`:

- Import yang diperlukan
- Class `RegistrasiDetailForm`
- `RegistrasiDetailFormSet`
- Class `RegistrasiFormMultiTerapi` (atau update `RegistrasiForm` yang ada)

### 3. Update Views (`core/views.py`)

Copy kode dari `CONTOH_VIEWS_MULTI_TERAPI.py` dan update `core/views.py`:

**Option A: Replace existing views**
- Ganti `RegistrasiCreateView` dengan `RegistrasiCreateViewMultiTerapi`
- Ganti `RegistrasiEditView` dengan `RegistrasiEditViewMultiTerapi`
- Tambahkan function `api_jenis_terapi_detail` untuk AJAX

**Option B: Keep both (recommended untuk testing)**
- Buat views baru dengan nama berbeda
- Test dulu sebelum fully replace

**Update ListView:**
```python
# Di RegistrasiListView.get_queryset(), tambahkan:
qs = qs.select_related(...).prefetch_related(
    'details',
    'details__jenis_terapi'
)
```

### 4. Update URLs (`core/urls.py`)

Copy konfigurasi dari `CONTOH_URLS.py`:

```python
# Tambahkan:
path('api/jenis-terapi/<int:pk>/', views.api_jenis_terapi_detail, name='api_jenis_terapi_detail'),

# Ganti atau tambah:
path('registrasi/tambah/', views.RegistrasiCreateViewMultiTerapi.as_view(), name='registrasi_create'),
path('registrasi/<int:pk>/edit/', views.RegistrasiEditViewMultiTerapi.as_view(), name='registrasi_edit'),
```

### 5. Create Template (`core/templates/core/`)

Copy `CONTOH_TEMPLATE_REGISTRASI_FORM_MULTI.html` ke:
```
core/templates/core/registrasi_form_multi.html
```

Atau jika mau replace yang lama, copy ke:
```
core/templates/core/registrasi_form.html
```

### 6. Update List Template (`core/templates/core/registrasi_list.html`)

Update bagian yang menampilkan jenis terapi menggunakan snippet dari `CONTOH_UPDATE_LIST_VIEW.html`:

```html
<!-- Ganti kolom "Jenis Terapi" dengan: -->
<td>
    {% if registrasi.details.exists %}
        {% for detail in registrasi.details.all %}
            <span class="badge bg-info mb-1">
                {{ detail.nama_terapi }}
                <small>(Rp {{ detail.harga_terapi|floatformat:0 }})</small>
            </span>
            {% if not forloop.last %}<br>{% endif %}
        {% endfor %}
    {% else %}
        <span class="badge bg-secondary">
            {{ registrasi.jenis_terapi.nama_terapi }}
        </span>
    {% endif %}
</td>
```

### 7. Create Migration Command (`core/management/commands/`)

Copy `CONTOH_MIGRATION_COMMAND.py` ke:
```
core/management/commands/migrate_to_multiterapi.py
```

### 8. Test Sistem Baru

#### Test 1: Input Registrasi Baru
```
1. Buka form registrasi baru
2. Pilih pasien, terapis, tanggal
3. Tambah beberapa terapi (klik "Tambah Terapi")
4. Pastikan harga ter-load otomatis
5. Pastikan total dihitung dengan benar
6. Submit dan cek di database
```

#### Test 2: Edit Registrasi
```
1. Edit registrasi yang sudah ada
2. Tambah/hapus terapi
3. Pastikan total ter-update
4. Submit dan cek hasilnya
```

#### Test 3: Display di List
```
1. Cek registrasi_list
2. Pastikan multiple terapi ditampilkan dengan benar
3. Cek badge/label untuk setiap terapi
```

### 9. Migrasi Data Lama (Optional)

Jika ada data registrasi lama yang belum punya detail:

```powershell
# Dry-run dulu (tidak mengubah data)
python manage.py migrate_to_multiterapi --dry-run

# Jika sudah OK, run actual migration
python manage.py migrate_to_multiterapi

# Jika mau force replace existing details
python manage.py migrate_to_multiterapi --force
```

## 🔍 Testing Checklist

- [ ] Migration berhasil dijalankan
- [ ] Form tampil dengan benar (header + detail terapi)
- [ ] Bisa tambah terapi baru (klik "Tambah Terapi")
- [ ] Bisa hapus terapi (minimal 1 harus tetap ada)
- [ ] Harga ter-load otomatis saat pilih jenis terapi
- [ ] Total harga dan total bayar ter-calculate dengan benar
- [ ] Bisa submit registrasi baru dengan multiple terapi
- [ ] Data tersimpan di table `registrasi` dan `registrasi_detail`
- [ ] Bisa edit registrasi dan tambah/hapus terapi
- [ ] List view menampilkan multiple terapi dengan benar
- [ ] Data lama (single terapi) tetap bisa ditampilkan (backward compatible)
- [ ] Command migrasi data lama berhasil

## 📊 Struktur Data

### Tabel `registrasi` (Header)
```
- id
- kode_registrasi
- pasien_id
- terapis_id
- tanggal_kunjungan
- harga (SUM dari registrasi_detail.harga_terapi)
- biaya_transport
- total_bayar (harga + biaya_transport)
- status
- cabang_id
- catatan
- created_by
- created_at
- updated_at
- is_deleted
```

### Tabel `registrasi_detail` (Detail)
```
- id
- registrasi_id (FK)
- kode_registrasi
- id_terapi (FK to jenis_terapi)
- nama_terapi
- harga_terapi
- remark
- remark2
- remark3
- created_date
```

## 🚨 Catatan Penting

1. **Backward Compatibility**: Field `jenis_terapi_id` dan `harga` di table `registrasi` masih ada untuk kompatibilitas dengan data lama. Jangan dihapus!

2. **Denormalisasi**: Field `nama_terapi` dan `harga_terapi` di `registrasi_detail` adalah denormalisasi - disimpan snapshot saat transaksi. Ini untuk:
   - Performa (tidak perlu JOIN setiap query)
   - Data historis (jika harga terapi berubah, data lama tetap accurate)

3. **Kalkulasi Total**: Total harga di header registrasi = SUM(registrasi_detail.harga_terapi)

4. **Validasi**: Minimal 1 terapi harus diinput (enforced by FormSet `min_num=1`)

5. **Transaction**: Simpan registrasi dan detail dalam 1 transaction (`@transaction.atomic`) untuk data consistency

## 🐛 Troubleshooting

### Error: "formset is not valid"
- Check browser console untuk JavaScript errors
- Check Django console untuk formset.errors
- Pastikan management_form ada di template

### Total tidak ter-calculate
- Check JavaScript console errors
- Pastikan jQuery loaded
- Pastikan API endpoint `/api/jenis-terapi/<id>/` berfungsi

### Data lama tidak muncul
- Jalankan migration command: `python manage.py migrate_to_multiterapi`
- Check apakah `registrasi.details.exists()` di template

### Harga tidak ter-load otomatis
- Check API endpoint berfungsi: buka `/api/jenis-terapi/1/` di browser
- Check network tab di browser (ada AJAX call?)
- Check CSRF token di AJAX request

## 📚 Referensi

- Django FormSets: https://docs.djangoproject.com/en/stable/topics/forms/formsets/
- Inline FormSets: https://docs.djangoproject.com/en/stable/topics/forms/modelforms/#inline-formsets
- Transactions: https://docs.djangoproject.com/en/stable/topics/db/transactions/

## 💡 Tips

1. **Development**: Test dengan data sample dulu sebelum production
2. **Backup**: Backup database sebelum run migration
3. **Logging**: Tambahkan logging untuk debugging
4. **UI/UX**: Bisa improve UI dengan drag-drop, autocomplete, dll
5. **Validasi**: Tambah validasi custom jika perlu (misal: max 10 terapi per registrasi)

## 🎯 Next Steps (Optional Enhancement)

- [ ] Tambah validation: max terapi per registrasi
- [ ] Tambah autocomplete/select2 untuk pilih terapi
- [ ] Tambah summary/preview sebelum submit
- [ ] Export to Excel/PDF dengan detail breakdown
- [ ] Report: Analisa terapi paling sering dipilih together
- [ ] Bulk operations: Copy terapi dari registrasi sebelumnya
