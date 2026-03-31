"""
Forms untuk Registrasi Multi-Terapi
Tambahkan kode ini ke file core/forms.py yang sudah ada
"""

from django import forms
from django.forms import inlineformset_factory
from .models import Registrasi, RegistrasiDetail, JenisTerapi

# Form untuk detail terapi individual
class RegistrasiDetailForm(forms.ModelForm):
    class Meta:
        model = RegistrasiDetail
        fields = ['jenis_terapi', 'remark', 'remark2', 'remark3']
        widgets = {
            'jenis_terapi': forms.Select(attrs={
                'class': 'form-select terapi-select',
                'required': True
            }),
            'remark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan...'
            }),
            'remark2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan tambahan...'
            }),
            'remark3': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan lainnya...'
            }),
        }

# FormSet untuk multiple terapi dalam satu registrasi
RegistrasiDetailFormSet = inlineformset_factory(
    Registrasi,
    RegistrasiDetail,
    form=RegistrasiDetailForm,
    extra=1,  # Jumlah form kosong yang ditampilkan
    can_delete=True,
    min_num=1,  # Minimal 1 terapi harus diinput
    validate_min=True,
    can_delete_extra=False  # Don't allow deleting the last empty form
)

# Update RegistrasiForm yang sudah ada
# Ubah fields agar tidak include 'jenis_terapi' dan 'harga' lagi
# karena akan dihandle oleh formset
class RegistrasiFormMultiTerapi(forms.ModelForm):
    """Form untuk header registrasi (tanpa jenis_terapi karena ada di detail)"""
    class Meta:
        model = Registrasi
        fields = ['pasien', 'terapis', 'tanggal_kunjungan', 'biaya_transport', 'is_transport', 'cabang', 'status', 'catatan']
        # Note: 'harga' akan dihitung otomatis dari sum detail terapi
        widgets = {
            'pasien': forms.Select(attrs={'class': 'form-select'}),
            'terapis': forms.Select(attrs={'class': 'form-select'}),
            'tanggal_kunjungan': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'biaya_transport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0', 'readonly': 'readonly'}),
            'is_transport': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cabang': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '-- Pilih Status --'),
                ('BOOKED', 'Booked'),
                ('CONFIRMED', 'Confirmed'),
                ('COMPLETED', 'Completed'),
                ('CANCELLED', 'Cancelled'),
            ]),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Catatan tambahan...'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        # If is_transport is False, set biaya_transport to 0
        if not instance.is_transport:
            instance.biaya_transport = Decimal('0.00')
        
        # Note: harga dan total_bayar akan diset di view setelah formset disimpan
        if commit:
            instance.save()
        return instance
