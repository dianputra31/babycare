# Update Template registrasi_form.html untuk Multi-Terapi

## Status Update
✅ Backend sudah siap (models, forms, views, URLs)
✅ Database migration sudah dijalankan  
✅ Template lama sudah di-backup ke `registrasi_form.html.backup`
⏳ Perlu update HTML template

## Cara Update Template

### 1. Edit file: `core/templates/core/registrasi_form.html`

### 2. Cari dan **HAPUS** section berikut (sekitar line 57-76 dan line 107-118):

```html
<!-- Jenis Terapi --> (HAPUS INI)
<div class="col-md-6">
  <label for="{{ form.jenis_terapi.id_for_label }}" class="form-label">
    Jenis Terapi <span class="text-danger">*</span>
  </label>
  ...
</div>

<!-- Harga --> (HAPUS INI JUGA)
<div class="col-md-6">
  <label for="{{ form.harga.id_for_label }}" class="form-label">
    Harga <span class="text-danger">*</span>
  </label>
  ...
</div>
```

### 3. TAMBAHKAN section baru setelah field "Catatan" (sebelum Biaya Transport):

```html
<!-- Detail Terapi (Multi-Terapi Section) -->
<div class="col-12 mt-4">
  <div class="border rounded-3 p-3" style="background-color: #f8f9fa;">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0">
        <i class="bi bi-list-check"></i> Detail Terapi
        <span class="badge bg-primary ms-2">Wajib minimal 1 terapi</span>
      </h5>
    </div>
    
    {{ formset.management_form }}
    
    <div id="terapi-formset">
      {% for form in formset %}
      <div class="terapi-form-row card mb-3" data-form-idx="{{ forloop.counter0 }}">
        <div class="card-body">
          {{ form.id }}
          <div class="row align-items-end">
            <div class="col-md-4 mb-2">
              <label class="form-label">Jenis Terapi <span class="text-danger">*</span></label>
              {{ form.jenis_terapi }}
              {% if form.jenis_terapi.errors %}
                <div class="text-danger small">{{ form.jenis_terapi.errors }}</div>
              {% endif %}
            </div>
            
            <div class="col-md-2 mb-2">
              <label class="form-label">Harga</label>
              <input type="text" class="form-control harga-display" readonly placeholder="Rp 0">
            </div>
            
            <div class="col-md-3 mb-2">
              <label class="form-label">Remark</label>
              {{ form.remark }}
            </div>
            
            <div class="col-md-2 mb-2">
              <label class="form-label">Remark 2</label>
              {{ form.remark2 }}
            </div>
            
            <div class="col-md-1 mb-2 text-end">
              {{ form.DELETE }}
              <button type="button" class="btn btn-danger btn-sm btn-remove-terapi" title="Hapus Terapi">
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
    
    <button type="button" id="add-terapi" class="btn btn-success mb-3">
      <i class="bi bi-plus-circle"></i> Tambah Terapi
    </button>
    
    <div class="alert alert-info">
      <div class="row">
        <div class="col-md-6">
          <strong>Total Harga Terapi: </strong>
          <span id="total-harga-terapi" class="fs-5">Rp 0</span>
        </div>
        <div class="col-md-6">
          <strong>Biaya Transport: </strong>
          <span id="biaya-transport-display" class="fs-5">Rp 0</span>
        </div>
      </div>
    </div>
  </div>
</div>
```

### 4. TAMBAHKAN JavaScript untuk formset di akhir section `<script>` (sebelum `</script>`):

```javascript
// ========================================
// Multi-Terapi Formset JavaScript
// ========================================
let formCount = parseInt($('#id_details-TOTAL_FORMS').val()) || 0;

// Initialize: Load harga for existing forms
$('.terapi-form-row').each(function() {
  let $row = $(this);
  let $select = $row.find('select[name*="jenis_terapi"]');
  if ($select.val()) {
    loadHargaTerapi($select);
  }
});

// Auto-populate harga saat jenis terapi dipilih
$(document).on('change', 'select[name*="jenis_terapi"]', function() {
  loadHargaTerapi($(this));
});

// Function to load harga via AJAX
function loadHargaTerapi($select) {
  let terapiId = $select.val();
  
  if (terapiId) {
    $.ajax({
      url: '/api/jenis-terapi/' + terapiId + '/',
      method: 'GET',
      success: function(data) {
        $select.closest('.terapi-form-row')
               .find('.harga-display')
               .val(data.harga_formatted)
               .data('harga', data.harga);
        calculateTotalTerapi();
      },
      error: function() {
        $select.closest('.terapi-form-row')
               .find('.harga-display')
               .val('Rp 0')
               .data('harga', 0);
        calculateTotalTerapi();
      }
    });
  } else {
    $select.closest('.terapi-form-row')
           .find('.harga-display')
           .val('Rp 0')
           .data('harga', 0);
    calculateTotalTerapi();
  }
}

// Tambah form terapi baru
$('#add-terapi').click(function() {
  let $templateRow = $('#terapi-formset .terapi-form-row').first().clone();
  
  // Update form indices
  $templateRow.attr('data-form-idx', formCount);
  $templateRow.find(':input').each(function() {
    let name = $(this).attr('name');
    let id = $(this).attr('id');
    
    if (name) {
      name = name.replace(/-\d+-/, `-${formCount}-`);
      $(this).attr('name', name);
    }
    if (id) {
      id = id.replace(/-\d+-/, `-${formCount}-`);
      $(this).attr('id', id);
    }
  });
  
  // Clear values
  $templateRow.find(':input:not([type=hidden])').val('');
  $templateRow.find('.harga-display').val('Rp 0').data('harga', 0);
  $templateRow.find('input[name*="DELETE"]').prop('checked', false);
  
  // Append to formset
  $('#terapi-formset').append($templateRow);
  
  // Update form count
  formCount++;
  $('#id_details-TOTAL_FORMS').val(formCount);
  
  calculateTotalTerapi();
});

// Hapus form terapi
$(document).on('click', '.btn-remove-terapi', function() {
  let $row = $(this).closest('.terapi-form-row');
  let $deleteInput = $row.find('input[name*="DELETE"]');
  
  // Check if this is the last visible row
  let visibleRows = $('.terapi-form-row:visible').length;
  if (visibleRows <= 1) {
    alert('Minimal 1 terapi harus dipilih!');
    return;
  }
  
  if ($deleteInput.length) {
    // Mark for deletion (for existing records)
    $deleteInput.prop('checked', true);
    $row.hide();
  } else {
    // Remove completely (for new forms)
    $row.remove();
  }
  
  calculateTotalTerapi();
});

// Monitor biaya transport changes
$('#id_biaya_transport, #id_is_transport').on('change', function() {
  calculateTotalTerapi();
});

// Hitung total terapi dan total bayar
function calculateTotalTerapi() {
  let totalHarga = 0;
  
  // Sum all visible terapi harga
  $('.terapi-form-row:visible').each(function() {
    let $deleteCheckbox = $(this).find('input[name*="DELETE"]');
    if (!$deleteCheckbox.prop('checked')) {
      let harga = parseFloat($(this).find('.harga-display').data('harga')) || 0;
      totalHarga += harga;
    }
  });
  
  // Get biaya transport
  let biayaTransport = 0;
  if ($('#id_is_transport').is(':checked')) {
    let transportVal = unformatNumber($('#id_biaya_transport').val());
    biayaTransport = parseFloat(transportVal) || 0;
  }
  
  let totalBayar = totalHarga + biayaTransport;
  
  // Update displays
  $('#total-harga-terapi').text(formatCurrency(totalHarga));
  $('#biaya-transport-display').text(formatCurrency(biayaTransport));
  $('#totalBayarDisplay').text(formatCurrency(totalBayar));
}

// Initial calculation
calculateTotalTerapi();
```

### 5. Test Sistem

1. Restart Django server kalau perlu
2. Buka: http://127.0.0.1:8000/registrasi/new/
3. Kamu akan lihat section "Detail Terapi" dengan button "Tambah Terapi"
4. Pilih terapi → harga akan load otomatis
5. Klik "Tambah Terapi" untuk menambah terapi lain
6. Total akan ter-calculate otomatis

## Troubleshooting

### Tombol "Tambah Terapi" tidak muncul
- Pastikan `{{ formset.management_form }}` ada di template
- Check browser console untuk JavaScript errors

### Harga tidak load otomatis
- Test API endpoint: http://127.0.0.1:8000/api/jenis-terapi/1/
- Check CSRF token
- Check browser console untuk AJAX errors

### Error saat save
- Check browser console
- Check Django console untuk formset errors
- Pastikan minimal 1 terapi dipilih

## File yang Sudah Diupdate

✅ `core/models.py` - Added RegistrasiDetail model  
✅ `core/forms.py` - Added RegistrasiDetailForm and FormSet   
✅ `core/views.py` - Updated RegistrasiCreateView & RegistrasiEditView  
✅ `core/urls.py` - Added API endpoint  
✅ `core/migrations/0005_registrasidetail.py` - Database migration  
⏳ `core/templates/core/registrasi_form.html` - Perlu update manual (lihat panduan di atas)

## Catatan

- Template lama sudah di-backup ke `registrasi_form.html.backup`
- Kalau ada masalah bisa restore: `Copy-Item registrasi_form.html.backup registrasi_form.html`
- Sistem backward compatible - data lama tetap bisa ditampilkan
