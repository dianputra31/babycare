from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator
from decimal import Decimal
from .models import Registrasi, RegistrasiDetail, Pemasukan, Pengeluaran, AppSettings, User, ProgressTracking, Role, Permission, RolePermission, UserRole, TemplatePesan, NOTIFICATION_TYPE_CHOICES
from .rbac import RESERVED_SUPERADMIN_ROLES, can_manage_roles, get_permission_groups_for_display, normalize_role_name, replace_role_permissions, replace_user_roles, sync_permission_catalog
from .services.registration_service import validate_age_for_terapi


class RegistrasiForm(forms.ModelForm):
    class Meta:
        model = Registrasi
        fields = ['pasien', 'terapis', 'tanggal_kunjungan', 'biaya_transport', 'is_transport', 'cabang', 'status', 'catatan']
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

    def clean(self):
        cleaned = super().clean()
        # Validation will be done in formset for multi-terapi
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # If is_transport is False, set biaya_transport to 0
        if not instance.is_transport:
            instance.biaya_transport = Decimal('0.00')
        
        # total_bayar will be calculated in view from formset
        if commit:
            instance.save()
        return instance


class PemasukanForm(forms.ModelForm):
    class Meta:
        model = Pemasukan
        fields = ['tanggal', 'registrasi', 'jumlah', 'jumlah_bayar', 'metode_pembayaran', 'keterangan']
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
        }

    def save(self, commit=True):
        """Auto-populate cabang from the selected registrasi"""
        instance = super().save(commit=False)
        if instance.registrasi:
            instance.cabang = instance.registrasi.cabang
        if commit:
            instance.save()
        return instance

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
    """Form for app settings (font size, logo, and notification settings)."""
    class Meta:
        model = AppSettings
        fields = [
            'font_size', 'logo',
            'enable_birthday_notif', 'birthday_notif_days_before',
            'enable_inactive_notif', 'inactive_threshold_days',
            'enable_followup_notif'
        ]
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
            'enable_birthday_notif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'birthday_notif_days_before': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '0',
                'max': '7'
            }),
            'enable_inactive_notif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'inactive_threshold_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '7'
            }),
            'enable_followup_notif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'font_size': 'Ukuran Font',
            'logo': 'Logo Aplikasi',
            'enable_birthday_notif': 'Aktifkan Notifikasi Ulang Tahun',
            'birthday_notif_days_before': 'Hari sebelum ulang tahun (H-1, H-2, dst)',
            'enable_inactive_notif': 'Aktifkan Notifikasi Pasien Tidak Aktif',
            'inactive_threshold_days': 'Jumlah hari untuk menandai pasien tidak aktif',
            'enable_followup_notif': 'Aktifkan Notifikasi Follow-up',
        }
        help_texts = {
            'font_size': 'Pilih ukuran font antara 10px hingga 24px',
            'logo': 'Upload logo untuk ditampilkan di header (format: JPG, PNG, max 2MB)',
            'birthday_notif_days_before': 'Berapa hari sebelum ulang tahun untuk mengirim notifikasi (0=hari H, 1=H-1, 2=H-2, dst)',
            'inactive_threshold_days': 'Pasien yang tidak registrasi dalam N hari akan mendapat notifikasi',
            'enable_followup_notif': 'Buat notifikasi reminder untuk follow-up pasien setelah registrasi'
        }


class ProgressTrackingForm(forms.ModelForm):
    class Meta:
        model = ProgressTracking
        fields = ['judul', 'catatan', 'foto_sebelum', 'foto_sesudah']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: Progress Sesi Ke-3'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Catatan hasil terapi, respon pasien, atau tindak lanjut...'}),
            'foto_sebelum': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'foto_sesudah': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        foto_sebelum = cleaned_data.get('foto_sebelum')
        foto_sesudah = cleaned_data.get('foto_sesudah')

        if not foto_sebelum and not foto_sesudah:
            raise ValidationError('Upload minimal satu foto progress: sebelum atau sesudah terapi.')

        return cleaned_data


class TemplatePesanForm(forms.ModelForm):
    tipe_pesan = forms.ChoiceField(
        choices=NOTIFICATION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = TemplatePesan
        fields = ['tipe_pesan', 'template_pesan']
        widgets = {
            'template_pesan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Contoh: Hi #pasien, sudah 1 bulan kita nggak ketemu, lho!'
            }),
        }
        labels = {
            'tipe_pesan': 'Tipe Pesan',
            'template_pesan': 'Template Pesan',
        }
        help_texts = {
            'template_pesan': 'Placeholder yang bisa dipakai: #pasien, #orang_tua, #tanggal, #kode_registrasi, #jenis_notifikasi',
        }

    def clean_tipe_pesan(self):
        tipe_pesan = self.cleaned_data['tipe_pesan']
        queryset = TemplatePesan.objects.filter(tipe_pesan=tipe_pesan)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError('Template untuk tipe pesan ini sudah ada. Silakan edit yang existing.')
        return tipe_pesan


class UserForm(forms.ModelForm):
    """Form for creating/editing users."""
    username_validator = RegexValidator(
        regex=r'^[A-Za-z0-9_]+$',
        message='Username harus 1 kata dan hanya boleh berisi huruf, angka, atau underscore (_).'
    )

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
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Role',
        help_text='Pilih satu atau lebih role untuk menentukan hak akses user ini.'
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'cabang', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: admin_babycare',
                'pattern': '[A-Za-z0-9_]+',
                'spellcheck': 'false',
                'autocomplete': 'off'
            }),
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
        help_texts = {
            'username': 'Wajib 1 kata, tanpa spasi, dan hanya boleh memakai huruf, angka, atau underscore (_).',
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user
        self.fields['roles'].queryset = Role.objects.all().order_by('nama_role')

        if self.instance and self.instance.pk:
            self.fields['roles'].initial = list(
                UserRole.objects.filter(user=self.instance).values_list('role_id', flat=True)
            )

        if not can_manage_roles(current_user):
            self.fields.pop('roles')

    def clean_username(self):
        username = (self.cleaned_data.get('username') or '').strip()
        self.username_validator(username)
        return username

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
            self.save_roles(user)
        
        return user

    def save_roles(self, user):
        if 'roles' not in self.fields:
            return

        selected_roles = self.cleaned_data.get('roles', Role.objects.none())
        replace_user_roles(user, selected_roles)


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


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Password Saat Ini',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'current-password'}),
    )
    new_password1 = forms.CharField(
        label='Password Baru',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text='Minimal 8 karakter dan sebaiknya kombinasi huruf, angka, atau simbol.',
    )
    new_password2 = forms.CharField(
        label='Konfirmasi Password Baru',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
    )


class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Privileges',
        help_text='Centang modul yang boleh diakses oleh role ini.'
    )

    class Meta:
        model = Role
        fields = ['nama_role', 'deskripsi']
        widgets = {
            'nama_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: admin operasional'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Jelaskan batasan role ini...'}),
        }
        labels = {
            'nama_role': 'Nama Role',
            'deskripsi': 'Deskripsi',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sync_permission_catalog()
        self.fields['permissions'].queryset = Permission.objects.all().order_by('module', 'action', 'code')
        self.permission_groups = get_permission_groups_for_display()

        if self.instance and self.instance.pk:
            self.fields['permissions'].initial = list(
                RolePermission.objects.filter(role=self.instance).values_list('permission_id', flat=True)
            )

    def clean_nama_role(self):
        nama_role = ' '.join((self.cleaned_data.get('nama_role') or '').split())
        if not nama_role:
            raise ValidationError('Nama role wajib diisi.')

        duplicate = Role.objects.filter(nama_role__iexact=nama_role)
        if self.instance and self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise ValidationError('Nama role sudah dipakai. Gunakan nama yang berbeda.')

        current_name = normalize_role_name(getattr(self.instance, 'nama_role', ''))
        if current_name in RESERVED_SUPERADMIN_ROLES and normalize_role_name(nama_role) != current_name:
            raise ValidationError('Role bawaan superadmin/owner tidak boleh diganti namanya.')

        return nama_role

    def get_selected_permission_ids(self):
        if self.is_bound:
            return {str(value) for value in self.data.getlist('permissions')}
        return {str(value) for value in self.initial.get('permissions', [])}

    def save(self, commit=True):
        role = super().save(commit=False)
        if commit:
            role.save()
            self.save_permissions(role)
        return role

    def save_permissions(self, role):
        if normalize_role_name(role.nama_role) in RESERVED_SUPERADMIN_ROLES:
            selected_permissions = Permission.objects.all()
        else:
            selected_permissions = self.cleaned_data.get('permissions', Permission.objects.none())

        replace_role_permissions(role, selected_permissions)


# ==========================================
# Forms untuk Registrasi Multi-Terapi
# ==========================================

class RegistrasiDetailForm(forms.ModelForm):
    """Form untuk detail terapi individual dalam registrasi"""
    class Meta:
        model = RegistrasiDetail
        fields = ['jenis_terapi', 'remark']
        widgets = {
            'jenis_terapi': forms.Select(attrs={
                'class': 'form-select terapi-select',
                'required': True
            }),
            'remark': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Catatan...'
            }),
        }

# FormSet untuk multiple terapi dalam satu registrasi
RegistrasiDetailFormSet = inlineformset_factory(
    Registrasi,
    RegistrasiDetail,
    form=RegistrasiDetailForm,
    extra=0,  # Tidak ada form kosong ekstra (akan dihandle via JavaScript)
    can_delete=True,
    min_num=1,  # Minimal 1 terapi harus diinput
    validate_min=True,
    can_delete_extra=False
)
