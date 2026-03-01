from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import Registrasi, Pemasukan, Pengeluaran, AppSettings, User
from .services.registration_service import validate_age_for_terapi


class RegistrasiForm(forms.ModelForm):
    class Meta:
        model = Registrasi
        fields = ['pasien', 'jenis_terapi', 'terapis', 'tanggal_kunjungan', 'harga', 'biaya_transport', 'cabang', 'status', 'catatan']
        widgets = {
            'pasien': forms.Select(attrs={'class': 'form-select'}),
            'jenis_terapi': forms.Select(attrs={'class': 'form-select'}),
            'terapis': forms.Select(attrs={'class': 'form-select'}),
            'tanggal_kunjungan': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'harga': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'biaya_transport': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0'}),
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

    def clean(self):
        cleaned = super().clean()
        pasien = cleaned.get('pasien')
        jenis = cleaned.get('jenis_terapi')
        tanggal = cleaned.get('tanggal_kunjungan')
        # validate umur pasien sesuai kategori terapi
        try:
            validate_age_for_terapi(pasien, jenis, reference_date=tanggal)
        except ValidationError as e:
            raise ValidationError({'pasien': e.message})
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.total_bayar = (instance.harga or 0) + (instance.biaya_transport or 0)
        if commit:
            instance.save()
        return instance


class PemasukanForm(forms.ModelForm):
    class Meta:
        model = Pemasukan
        fields = ['tanggal', 'registrasi', 'jumlah', 'jumlah_bayar', 'metode_pembayaran', 'keterangan', 'cabang']
        widgets = {
            'tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'registrasi': forms.Select(attrs={'class': 'form-select'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'jumlah_bayar': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'metode_pembayaran': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '-- Pilih Metode --'),
                ('TUNAI', 'Tunai'),
                ('TRANSFER', 'Transfer'),
                ('QRIS', 'QRIS'),
                ('DEBIT', 'Debit'),
                ('KREDIT', 'Kredit'),
            ]),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Keterangan...'}),
            'cabang': forms.Select(attrs={'class': 'form-select'}),
        }

    # permission checks happen on the view level (requires request)


class PengeluaranForm(forms.ModelForm):
    KATEGORI_CHOICES = [
        ('', '-- Pilih Kategori --'),
        ('Minyak Pijat', 'Minyak Pijat'),
        ('Shampoo Bayi', 'Shampoo Bayi'),
        ('Sabun Bayi', 'Sabun Bayi'),
        ('Bedak', 'Bedak'),
        ('Tisu Basah', 'Tisu Basah'),
        ('Popok', 'Popok'),
        ('Lotion Bayi', 'Lotion Bayi'),
        ('Baby Oil', 'Baby Oil'),
        ('Minyak Telon', 'Minyak Telon'),
        ('Handuk', 'Handuk'),
        ('Selimut', 'Selimut'),
        ('Kasur/Matras', 'Kasur/Matras'),
        ('Alat Terapi', 'Alat Terapi'),
        ('Listrik', 'Listrik'),
        ('Air', 'Air'),
        ('Internet', 'Internet'),
        ('Gaji Karyawan', 'Gaji Karyawan'),
        ('Kebersihan', 'Kebersihan'),
        ('Perawatan Gedung', 'Perawatan Gedung'),
        ('Lainnya', 'Lainnya'),
    ]
    
    kategori = forms.ChoiceField(
        choices=KATEGORI_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    
    class Meta:
        model = Pengeluaran
        fields = ['tanggal', 'kategori', 'jumlah', 'keterangan', 'cabang']
        widgets = {
            'tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'jumlah': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'keterangan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Keterangan...'}),
            'cabang': forms.Select(attrs={'class': 'form-select'}),
        }


class AppSettingsForm(forms.ModelForm):
    """Form for app settings (font size and logo)."""
    class Meta:
        model = AppSettings
        fields = ['font_size', 'logo']
        widgets = {
            'font_size': forms.NumberInput(attrs={
                'class': 'form-range',
                'type': 'range',
                'min': '10',
                'max': '24',
                'step': '1',
                'id': 'fontSizeSlider'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'font_size': 'Ukuran Font',
            'logo': 'Logo Aplikasi'
        }
        help_texts = {
            'font_size': 'Pilih ukuran font antara 10px hingga 24px',
            'logo': 'Upload logo untuk ditampilkan di header (format: JPG, PNG, max 2MB)'
        }


class UserForm(forms.ModelForm):
    """Form for creating/editing users."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text='Kosongkan jika tidak ingin mengubah password'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label='Konfirmasi Password'
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'cabang', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cabang': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Username',
            'full_name': 'Nama Lengkap',
            'email': 'Email',
            'cabang': 'Cabang',
            'is_active': 'Aktif'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise ValidationError({'password_confirm': 'Password tidak cocok'})

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user


class UserCreateForm(UserForm):
    """Form specifically for creating new users (password is required)."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        help_text='Masukkan password untuk user baru'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
        label='Konfirmasi Password'
    )
