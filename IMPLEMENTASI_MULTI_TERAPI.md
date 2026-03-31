# Panduan Implementasi Sistem Registrasi Multi-Terapi

## 1. Model (✅ SELESAI)

Model `RegistrasiDetail` telah dibuat di `core/models.py`:
- Menyimpan detail setiap terapi dalam satu registrasi
- Relasi: `registrasi.details` untuk mengakses semua terapi dalam registrasi
- Field penting: `jenis_terapi`, `nama_terapi`, `harga_terapi`

## 2. Perubahan Form dan Views

### A. Form untuk Input Multi-Terapi

Perlu membuat FormSet untuk input multiple terapi:

```python
# core/forms.py

from django.forms import modelformset_factory, inlineformset_factory

# FormSet untuk detail terapi (multiple terapi per registrasi)
RegistrasiDetailFormSet = inlineformset_factory(
    Registrasi,
    RegistrasiDetail,
    fields=['jenis_terapi', 'remark', 'remark2', 'remark3'],
    extra=1,  # Jumlah form kosong yang ditampilkan
    can_delete=True,
    min_num=1,  # Minimal 1 terapi harus diinput
    validate_min=True
)
```

### B. View untuk Create/Update Registrasi

Perlu mengubah view registrasi untuk handle FormSet:

```python
# core/views.py

@login_required
@permission_required('registrasi.create')
def registrasi_form(request, pk=None):
    if pk:
        registrasi = get_object_or_404(Registrasi, pk=pk)
    else:
        registrasi = None
    
    if request.method == 'POST':
        form = RegistrasiForm(request.POST, instance=registrasi)
        formset = RegistrasiDetailFormSet(request.POST, instance=registrasi or Registrasi())
        
        if form.is_valid() and formset.is_valid():
            # Simpan header registrasi
            registrasi = form.save(commit=False)
            registrasi.created_by = request.user
            
            # Hitung total dari semua terapi
            total_harga = Decimal('0.00')
            for detail_form in formset:
                if detail_form.cleaned_data and not detail_form.cleaned_data.get('DELETE'):
                    jenis_terapi = detail_form.cleaned_data['jenis_terapi']
                    total_harga += jenis_terapi.harga
            
            # Set harga dan total_bayar
            registrasi.harga = total_harga
            registrasi.total_bayar = calculate_total_bayar(total_harga, registrasi.biaya_transport)
            registrasi.save()
            
            # Simpan detail terapi
            details = formset.save(commit=False)
            for detail in details:
                detail.registrasi = registrasi
                detail.kode_registrasi = registrasi.kode_registrasi
                detail.nama_terapi = detail.jenis_terapi.nama_terapi
                detail.harga_terapi = detail.jenis_terapi.harga
                detail.save()
            
            # Hapus detail yang dimarkah DELETE
            for obj in formset.deleted_objects:
                obj.delete()
            
            messages.success(request, 'Registrasi berhasil disimpan')
            return redirect('core:registrasi_list')
    else:
        form = RegistrasiForm(instance=registrasi)
        formset = RegistrasiDetailFormSet(instance=registrasi or Registrasi())
    
    context = {
        'form': form,
        'formset': formset,
        'is_edit': pk is not None
    }
    return render(request, 'core/registrasi_form.html', context)
```

## 3. Template/UI Changes

### A. Form Template dengan Dynamic FormSet

```html
<!-- core/templates/core/registrasi_form.html -->

<form method="post" id="registrasi-form">
    {% csrf_token %}
    
    <!-- Form Header (Pasien, Terapis, Tanggal, dll) -->
    <div class="form-section">
        <h3>Data Registrasi</h3>
        {{ form.as_p }}
    </div>
    
    <!-- FormSet untuk Multi-Terapi -->
    <div class="form-section">
        <h3>Detail Terapi</h3>
        {{ formset.management_form }}
        
        <div id="terapi-formset">
            {% for form in formset %}
                <div class="terapi-form-row">
                    {{ form.id }}
                    <div class="row">
                        <div class="col-md-4">
                            {{ form.jenis_terapi.label_tag }}
                            {{ form.jenis_terapi }}
                        </div>
                        <div class="col-md-2">
                            <label>Harga</label>
                            <input type="text" class="form-control harga-display" readonly>
                        </div>
                        <div class="col-md-3">
                            {{ form.remark.label_tag }}
                            {{ form.remark }}
                        </div>
                        <div class="col-md-2">
                            {% if not forloop.first %}
                            <button type="button" class="btn btn-danger btn-remove-terapi">
                                Hapus
                            </button>
                            {% endif %}
                        </div>
                    </div>
                    {{ form.DELETE }}
                </div>
            {% endfor %}
        </div>
        
        <button type="button" id="add-terapi" class="btn btn-success">
            + Tambah Terapi
        </button>
        
        <div class="total-section mt-3">
            <strong>Total Harga Terapi: </strong>
            <span id="total-harga">Rp 0</span>
        </div>
    </div>
    
    <button type="submit" class="btn btn-primary">Simpan</button>
</form>

<script>
$(document).ready(function() {
    // Auto-populate harga saat jenis terapi dipilih
    $(document).on('change', 'select[name*="jenis_terapi"]', function() {
        var $select = $(this);
        var terapiId = $select.val();
        
        if (terapiId) {
            $.ajax({
                url: '/api/jenis-terapi/' + terapiId + '/',
                success: function(data) {
                    $select.closest('.terapi-form-row')
                           .find('.harga-display')
                           .val('Rp ' + data.harga.toLocaleString('id-ID'));
                    calculateTotal();
                }
            });
        }
    });
    
    // Tambah form terapi baru
    $('#add-terapi').click(function() {
        var formCount = parseInt($('#id_details-TOTAL_FORMS').val());
        var newForm = $('#terapi-formset .terapi-form-row:first').clone();
        
        // Update form index
        newForm.find(':input').each(function() {
            var name = $(this).attr('name');
            if (name) {
                name = name.replace('-0-', '-' + formCount + '-');
                $(this).attr('name', name);
                $(this).attr('id', 'id_' + name);
            }
        });
        
        // Clear values
        newForm.find(':input').val('');
        newForm.find('.harga-display').val('');
        
        $('#terapi-formset').append(newForm);
        $('#id_details-TOTAL_FORMS').val(formCount + 1);
    });
    
    // Hapus form terapi
    $(document).on('click', '.btn-remove-terapi', function() {
        var $row = $(this).closest('.terapi-form-row');
        $row.find('input[name*="DELETE"]').val('on');
        $row.hide();
        calculateTotal();
    });
    
    // Hitung total
    function calculateTotal() {
        var total = 0;
        $('.terapi-form-row:visible').each(function() {
            var hargaText = $(this).find('.harga-display').val();
            if (hargaText) {
                var harga = parseFloat(hargaText.replace(/[^0-9]/g, ''));
                total += harga;
            }
        });
        $('#total-harga').text('Rp ' + total.toLocaleString('id-ID'));
    }
});
</script>
```

## 4. API Endpoint untuk Get Harga Terapi

```python
# core/views.py

@login_required
def api_jenis_terapi_detail(request, pk):
    """API endpoint untuk get detail jenis terapi (untuk AJAX)"""
    terapi = get_object_or_404(JenisTerapi, pk=pk)
    return JsonResponse({
        'id': terapi.id,
        'nama_terapi': terapi.nama_terapi,
        'harga': float(terapi.harga)
    })
```

```python
# core/urls.py
urlpatterns = [
    # ... existing urls
    path('api/jenis-terapi/<int:pk>/', views.api_jenis_terapi_detail, name='api_jenis_terapi_detail'),
]
```

## 5. Update Display di List dan Detail View

### A. Registrasi List - Tampilkan Multiple Terapi

```html
<!-- Dalam registrasi_list.html -->
<td>
    {% for detail in registrasi.details.all %}
        <span class="badge bg-info">{{ detail.nama_terapi }}</span>
        {% if not forloop.last %}<br>{% endif %}
    {% empty %}
        <span class="text-muted">{{ registrasi.jenis_terapi.nama_terapi }}</span>
    {% endfor %}
</td>
```

### B. Detail View - Tampilkan Breakdown Terapi

```html
<!-- Detail registrasi -->
<h4>Detail Terapi</h4>
<table class="table">
    <thead>
        <tr>
            <th>Terapi</th>
            <th>Harga</th>
            <th>Remark</th>
        </tr>
    </thead>
    <tbody>
        {% for detail in registrasi.details.all %}
        <tr>
            <td>{{ detail.nama_terapi }}</td>
            <td>Rp {{ detail.harga_terapi|floatformat:0|intcomma }}</td>
            <td>{{ detail.remark|default:"-" }}</td>
        </tr>
        {% empty %}
        <tr>
            <td colspan="3" class="text-center text-muted">
                Belum ada detail terapi (mungkin data lama)
            </td>
        </tr>
        {% endfor %}
        <tr class="table-info">
            <td><strong>Total Harga Terapi</strong></td>
            <td><strong>Rp {{ registrasi.harga|floatformat:0|intcomma }}</strong></td>
            <td></td>
        </tr>
        <tr>
            <td>Biaya Transport</td>
            <td>Rp {{ registrasi.biaya_transport|floatformat:0|intcomma }}</td>
            <td></td>
        </tr>
        <tr class="table-success">
            <td><strong>TOTAL BAYAR</strong></td>
            <td><strong>Rp {{ registrasi.total_bayar|floatformat:0|intcomma }}</strong></td>
            <td></td>
        </tr>
    </tbody>
</table>
```

## 6. Migrasi Data Lama (Optional)

Jika ada data registrasi lama yang belum punya detail, perlu dibuat script untuk migrasi:

```python
# Management command: core/management/commands/migrate_registrasi_to_detail.py

from django.core.management.base import BaseCommand
from core.models import Registrasi, RegistrasiDetail

class Command(BaseCommand):
    help = 'Migrate existing registrasi to use registrasi_detail'

    def handle(self, *args, **options):
        registrasis = Registrasi.objects.filter(is_deleted=False)
        migrated = 0
        
        for reg in registrasis:
            # Cek apakah sudah punya detail
            if not reg.details.exists():
                # Buat detail dari data lama
                RegistrasiDetail.objects.create(
                    registrasi=reg,
                    kode_registrasi=reg.kode_registrasi,
                    jenis_terapi=reg.jenis_terapi,
                    nama_terapi=reg.jenis_terapi.nama_terapi,
                    harga_terapi=reg.harga
                )
                migrated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully migrated {migrated} registrasi records')
        )
```

Jalankan dengan: `python manage.py migrate_registrasi_to_detail`

## 7. Checklist Implementasi

- [x] Buat model RegistrasiDetail
- [x] Buat migration file
- [ ] Buat FormSet di forms.py
- [ ] Update view registrasi_form untuk handle formset
- [ ] Update template registrasi_form.html dengan dynamic formset
- [ ] Tambah API endpoint untuk get harga terapi
- [ ] Update registrasi_list.html untuk tampilkan multi-terapi
- [ ] Buat detail view yang menampilkan breakdown terapi
- [ ] Test input registrasi baru dengan multiple terapi
- [ ] Test edit registrasi dengan tambah/hapus terapi
- [ ] (Optional) Migrasi data lama

## 8. Catatan Penting

1. **Backward Compatibility**: Field `jenis_terapi` dan `harga` di tabel `registrasi` tetap ada untuk backward compatibility dengan data lama.

2. **Kalkulasi Total**: Harga di header `registrasi` akan dihitung sebagai SUM dari semua `harga_terapi` di `registrasi_detail`.

3. **Denormalisasi**: Field `nama_terapi` dan `harga_terapi` di `registrasi_detail` adalah denormalisasi untuk performa dan historis (jika harga terapi berubah, data historis tetap).

4. **UI/UX**: Gunakan JavaScript/jQuery untuk dynamic form (add/remove terapi) dan auto-calculate total.

5. **Validasi**: Pastikan minimal 1 terapi harus diinput (gunakan `min_num=1` di FormSet).
