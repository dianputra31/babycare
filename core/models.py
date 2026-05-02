# e:/projects/python/django/teguh/babycare/core/models.py
from django.db import models, transaction
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from decimal import Decimal
from .services.registration_service import calculate_total_bayar


def progress_upload_path(instance, filename):
    return f'progress/{instance.registrasi_id}/{filename}'


NOTIFICATION_TYPE_CHOICES = [
    ('BIRTHDAY', '🎂 Ulang Tahun'),
    ('INACTIVE_30D', '⏰ Pasien Tidak Aktif (1 bulan)'),
    ('INACTIVE_90D', '⏰ Pasien Tidak Aktif (3 bulan)'),
    ('INACTIVE_180D', '⏰ Pasien Tidak Aktif (6 bulan)'),
    ('FOLLOWUP', '📋 Follow-up'),
    ('HIGH_POTENTIAL', '⭐ High Potential'),
    ('APPOINTMENT_REMINDER', '📅 Reminder Jadwal'),
]

DEFAULT_MESSAGE_TEMPLATES = {
    'BIRTHDAY': 'Hi #pasien, selamat ulang tahun ya! Semoga sehat selalu dan tumbuh makin hebat bersama Babycare.',
    'INACTIVE_30D': 'Hi #pasien, sudah 1 bulan kita nggak ketemu, lho! Bulan ini kami ada penawaran paket special buatmu!',
    'INACTIVE_90D': 'Hi #pasien, sudah 3 bulan kita tidak bertemu. Kalau mau mulai lagi, kami siap bantu dengan program yang sesuai kebutuhanmu.',
    'INACTIVE_180D': 'Hi #pasien, sudah 6 bulan sejak sesi terakhir. Yuk lanjutkan lagi bersama Babycare, kami punya penawaran khusus untukmu.',
    'FOLLOWUP': 'Hi #orang_tua, bagaimana kabar #pasien setelah sesi terakhir? Kami siap bantu follow-up atau atur jadwal berikutnya.',
    'HIGH_POTENTIAL': 'Hi #orang_tua, terima kasih sudah rutin bersama Babycare untuk #pasien. Saat ini ada paket spesial yang mungkin cocok untuk lanjutan terapinya.',
    'APPOINTMENT_REMINDER': 'Hi #orang_tua, ini reminder ya. #pasien dijadwalkan terapi pada #tanggal. Sampai bertemu di Babycare.',
}


def render_notification_message(template_text, notification=None):
    pasien = getattr(notification, 'pasien', None)
    registrasi = getattr(notification, 'registrasi', None)
    replacements = {
        '#pasien': getattr(pasien, 'nama_anak', '') or '',
        '#orang_tua': getattr(pasien, 'nama_orang_tua', '') or 'Bapak/Ibu',
        '#tanggal': registrasi.tanggal_kunjungan.strftime('%d %b %Y') if registrasi and registrasi.tanggal_kunjungan else '',
        '#kode_registrasi': getattr(registrasi, 'kode_registrasi', '') or '',
        '#jenis_notifikasi': getattr(notification, 'jenis_notifikasi', '') or '',
    }

    rendered = template_text or ''
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered.strip()

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        user = self.create_user(username, password, **extra_fields)
        return user

class Cabang(models.Model):
    id = models.BigAutoField(primary_key=True)
    nama_cabang = models.CharField(max_length=100, db_column='nama_cabang')
    alamat = models.TextField(db_column='alamat', null=True, blank=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta:
        db_table = 'cabang'
        managed = False

    def __str__(self):
        return self.nama_cabang

class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    nama_role = models.CharField(max_length=50, db_column='nama_role')
    deskripsi = models.TextField(db_column='deskripsi', null=True, blank=True)

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.nama_role

class Permission(models.Model):
    id = models.BigAutoField(primary_key=True)
    module = models.CharField(max_length=100, db_column='module')
    action = models.CharField(max_length=50, db_column='action')
    code = models.CharField(max_length=150, db_column='code', unique=True)

    class Meta:
        db_table = 'permissions'
        managed = False

    def __str__(self):
        return self.code

class RolePermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    role = models.ForeignKey(Role, db_column='role_id', on_delete=models.DO_NOTHING)
    permission = models.ForeignKey(Permission, db_column='permission_id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'role_permissions'
        managed = False

class UserRole(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('User', db_column='user_id', on_delete=models.DO_NOTHING)
    role = models.ForeignKey(Role, db_column='role_id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'user_roles'
        managed = False

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, db_column='password_hash')
    full_name = models.CharField(max_length=255, db_column='full_name', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True, db_column='is_active')
    created_at = models.DateTimeField(db_column='created_at', blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'
        managed = True

    def __str__(self):
        return self.username

    def get_roles(self):
        return Role.objects.filter(userrole__user=self)

    @property
    def role_names(self):
        return {role.nama_role.strip().lower() for role in self.get_roles() if role.nama_role}

    @property
    def is_superadmin_role(self):
        return self.is_superuser or bool({'superadmin', 'owner'} & self.role_names)

    def get_permissions(self):
        if self.is_superadmin_role:
            return Permission.objects.all()
        return Permission.objects.filter(rolepermission__role__userrole__user=self).distinct()

    def has_permission(self, code: str) -> bool:
        if not self.is_authenticated:
            return False
        if self.is_superadmin_role:
            return True
        return Permission.objects.filter(code=code, rolepermission__role__userrole__user=self).exists()

class Pasien(models.Model):
    id = models.BigAutoField(primary_key=True)
    kode_pasien = models.CharField(max_length=20, db_column='kode_pasien', null=True, blank=True, unique=True)
    nama_anak = models.CharField(max_length=150, db_column='nama_anak')
    tanggal_lahir = models.DateField(db_column='tanggal_lahir')
    jenis_kelamin = models.CharField(max_length=1, db_column='jenis_kelamin', null=True, blank=True, choices=[('L', 'Laki-laki'), ('P', 'Perempuan')])
    nama_orang_tua = models.CharField(max_length=150, db_column='nama_orang_tua', null=True, blank=True)
    alamat = models.TextField(db_column='alamat', null=True, blank=True)
    no_wa = models.CharField(max_length=20, db_column='no_wa', null=True, blank=True)
    has_whatsapp = models.BooleanField(db_column='has_whatsapp', default=False, help_text='Nomor terdaftar di WhatsApp')
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)

    class Meta:
        db_table = 'pasien'
        managed = False

    def __str__(self):
        return self.nama_anak

class JenisTerapi(models.Model):
    id = models.BigAutoField(primary_key=True)
    nama_terapi = models.CharField(max_length=200, db_column='nama_terapi')
    harga = models.DecimalField(max_digits=12, decimal_places=2, db_column='harga')
    kategori_usia_min = models.DecimalField(max_digits=4, decimal_places=1, db_column='kategori_usia_min', null=True, blank=True)
    kategori_usia_max = models.DecimalField(max_digits=4, decimal_places=1, db_column='kategori_usia_max', null=True, blank=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)

    class Meta:
        db_table = 'jenis_terapi'
        managed = False

    def __str__(self):
        return self.nama_terapi

class Terapis(models.Model):
    id = models.BigAutoField(primary_key=True)
    nama_terapis = models.CharField(max_length=150, db_column='nama_terapis')
    no_hp = models.CharField(max_length=20, db_column='no_hp', null=True, blank=True)
    alamat = models.TextField(db_column='alamat', null=True, blank=True)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    biaya_transport_default = models.DecimalField(max_digits=12, decimal_places=2, db_column='biaya_transport_default', default=Decimal('0.00'))
    is_active = models.BooleanField(db_column='is_active', default=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)

    class Meta:
        db_table = 'terapis'
        managed = False

    def __str__(self):
        return self.nama_terapis

class Registrasi(models.Model):
    id = models.BigAutoField(primary_key=True)
    kode_registrasi = models.CharField(max_length=20, db_column='kode_registrasi', null=True, blank=True, unique=True)
    pasien = models.ForeignKey(Pasien, db_column='pasien_id', on_delete=models.DO_NOTHING)
    jenis_terapi = models.ForeignKey(JenisTerapi, db_column='jenis_terapi_id', on_delete=models.DO_NOTHING)
    terapis = models.ForeignKey(Terapis, db_column='terapis_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    tanggal_kunjungan = models.DateField(db_column='tanggal_kunjungan')
    jam_kunjungan = models.TimeField(db_column='jam_kunjungan', null=True, blank=True)
    status = models.CharField(max_length=20, db_column='status', default='BOOKED')
    harga = models.DecimalField(db_column='harga', max_digits=12, decimal_places=2)
    biaya_transport = models.DecimalField(db_column='biaya_transport', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_bayar = models.DecimalField(db_column='total_bayar', max_digits=12, decimal_places=2, null=True, blank=True)
    catatan = models.TextField(db_column='catatan', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='registrasi_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)
    is_transport = models.BooleanField(db_column='is_transport', default=True)

    class Meta:
        db_table = 'registrasi'
        managed = False

    def __str__(self):
        return f"Registrasi #{self.id} - {self.pasien}"

    def save(self, *args, **kwargs):
        self.total_bayar = calculate_total_bayar(self.harga, self.biaya_transport)
        super().save(*args, **kwargs)

class RegistrasiDetail(models.Model):
    """Detail terapi dalam satu registrasi (multi-terapi support)"""
    id = models.BigAutoField(primary_key=True)
    registrasi = models.ForeignKey(Registrasi, db_column='registrasi_id', on_delete=models.CASCADE, related_name='details')
    kode_registrasi = models.CharField(max_length=255, db_column='kode_registrasi', null=True, blank=True)
    jenis_terapi = models.ForeignKey(JenisTerapi, db_column='id_terapi', on_delete=models.DO_NOTHING)
    nama_terapi = models.CharField(max_length=255, db_column='nama_terapi', null=True, blank=True)
    harga_terapi = models.DecimalField(max_digits=12, decimal_places=0, db_column='harga_terapi', null=True, blank=True)
    remark = models.CharField(max_length=255, db_column='remark', null=True, blank=True)
    created_date = models.DateTimeField(db_column='created_date', auto_now_add=True)
    remark2 = models.CharField(max_length=255, db_column='remark2', null=True, blank=True)
    remark3 = models.CharField(max_length=255, db_column='remark3', null=True, blank=True)

    class Meta:
        db_table = 'registrasi_detail'
        managed = True  # Changed to True since this is our own table

    def __str__(self):
        return f"{self.kode_registrasi} - {self.nama_terapi}"


class ProgressTracking(models.Model):
    id = models.BigAutoField(primary_key=True)
    registrasi = models.ForeignKey(Registrasi, db_column='registrasi_id', on_delete=models.CASCADE, related_name='progress_entries')
    judul = models.CharField(max_length=150, db_column='judul')
    catatan = models.TextField(db_column='catatan', null=True, blank=True)
    foto_sebelum = models.ImageField(db_column='foto_sebelum', upload_to=progress_upload_path, null=True, blank=True)
    foto_sesudah = models.ImageField(db_column='foto_sesudah', upload_to=progress_upload_path, null=True, blank=True)
    created_by = models.ForeignKey('User', db_column='created_by', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='progress_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta:
        db_table = 'progress_tracking'
        managed = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.registrasi.kode_registrasi} - {self.judul}"

class Pemasukan(models.Model):
    id = models.BigAutoField(primary_key=True)
    registrasi = models.ForeignKey(Registrasi, db_column='registrasi_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    tanggal = models.DateField(db_column='tanggal', null=True, blank=True)
    jumlah = models.DecimalField(max_digits=12, decimal_places=2, db_column='jumlah')
    jumlah_bayar = models.DecimalField(max_digits=12, decimal_places=2, db_column='jumlah_bayar', null=True, blank=True)
    metode_pembayaran = models.CharField(max_length=50, db_column='metode_pembayaran', null=True, blank=True)
    keterangan = models.TextField(db_column='keterangan', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='pemasukan_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta:
        db_table = 'pemasukan'
        managed = False

    def __str__(self):
        return f"Pemasukan #{self.id} - {self.jumlah}"

class Pengeluaran(models.Model):
    id = models.BigAutoField(primary_key=True)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    tanggal = models.DateField(db_column='tanggal', null=True, blank=True)
    kategori = models.CharField(max_length=100, db_column='kategori', null=True, blank=True)
    jumlah = models.DecimalField(max_digits=12, decimal_places=2, db_column='jumlah')
    keterangan = models.TextField(db_column='keterangan', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='pengeluaran_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    
    # Inventory Integration Fields
    barang = models.ForeignKey('BarangInventory', db_column='barang_id', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='pengeluaran_set', verbose_name='Barang Inventory')
    jumlah_barang = models.IntegerField(db_column='jumlah_barang', null=True, blank=True, verbose_name='Jumlah Barang')
    harga_satuan_beli = models.DecimalField(max_digits=12, decimal_places=2, db_column='harga_satuan_beli', null=True, blank=True, verbose_name='Harga Beli/Satuan')
    supplier = models.CharField(max_length=200, db_column='supplier', null=True, blank=True, verbose_name='Supplier')
    no_faktur = models.CharField(max_length=100, db_column='no_faktur', null=True, blank=True, verbose_name='No. Faktur')

    class Meta:
        db_table = 'pengeluaran'
        managed = True

class TransportTerapis(models.Model):
    id = models.BigAutoField(primary_key=True)
    registrasi = models.ForeignKey(Registrasi, db_column='registrasi_id', on_delete=models.DO_NOTHING)
    terapis = models.ForeignKey(Terapis, db_column='terapis_id', on_delete=models.DO_NOTHING)
    jumlah_transport = models.DecimalField(max_digits=12, decimal_places=2, db_column='jumlah_transport')
    tanggal = models.DateField(db_column='tanggal', auto_now_add=True)

    class Meta:
        db_table = 'transport_terapis'
        managed = False

class Notifikasi(models.Model):
    id = models.BigAutoField(primary_key=True)
    pasien = models.ForeignKey(Pasien, db_column='pasien_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    registrasi = models.ForeignKey(Registrasi, db_column='registrasi_id', null=True, blank=True, on_delete=models.DO_NOTHING)
    jenis_notifikasi = models.CharField(max_length=50, db_column='jenis_notifikasi', null=True, blank=True)
    pesan = models.TextField(db_column='pesan', null=True, blank=True)
    tanggal_notifikasi = models.DateField(db_column='tanggal_notifikasi', null=True, blank=True)
    sudah_dibaca = models.BooleanField(db_column='sudah_dibaca', default=False)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta:
        db_table = 'notifikasi'
        managed = False

    def __str__(self):
        return f"{self.jenis_notifikasi} - {self.pesan[:50] if self.pesan else ''}"


class TemplatePesan(models.Model):
    id = models.BigAutoField(primary_key=True)
    tipe_pesan = models.CharField(max_length=255, db_column='tipe_pesan')
    template_pesan = models.CharField(max_length=255, db_column='template_pesan')

    class Meta:
        db_table = 'template_pesan'
        managed = False

    def __str__(self):
        return self.tipe_pesan or f'Template #{self.pk}'

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                max_id = TemplatePesan.objects.aggregate(max_id=models.Max('id'))['max_id'] or 0
                self.id = max_id + 1
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)

    @classmethod
    def get_template_for_type(cls, tipe_pesan):
        return cls.objects.filter(tipe_pesan=tipe_pesan).first()

    @classmethod
    def build_message_for_notification(cls, notification):
        tipe_pesan = getattr(notification, 'jenis_notifikasi', None)
        template = cls.get_template_for_type(tipe_pesan)
        if template and template.template_pesan:
            return render_notification_message(template.template_pesan, notification)
        if tipe_pesan in DEFAULT_MESSAGE_TEMPLATES:
            return render_notification_message(DEFAULT_MESSAGE_TEMPLATES[tipe_pesan], notification)
        return getattr(notification, 'pesan', '') or ''


class AppSettings(models.Model):
    """Global application settings like font size and logo."""
    
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
        ('blue', 'Blue Theme'),
        ('green', 'Green Theme'),
        ('purple', 'Purple Theme'),
        ('orange', 'Orange Theme'),
    ]
    
    id = models.AutoField(primary_key=True)
    font_size = models.IntegerField(default=14, help_text='Font size in pixels (default: 14)')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, help_text='Upload logo image')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light', help_text='Color theme aplikasi')
    
    # Notification settings
    birthday_notif_days_before = models.IntegerField(default=1, help_text='Hari sebelum ulang tahun untuk notifikasi (1=H-1, 2=H-2)')
    inactive_threshold_days = models.IntegerField(default=30, help_text='Hari inaktif untuk notifikasi pasien (default: 30 hari)')
    enable_birthday_notif = models.BooleanField(default=True, help_text='Aktifkan notifikasi ulang tahun')
    enable_inactive_notif = models.BooleanField(default=True, help_text='Aktifkan notifikasi pasien tidak aktif')
    enable_followup_notif = models.BooleanField(default=True, help_text='Aktifkan notifikasi follow-up registrasi')
    
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='settings_updated')

    class Meta:
        db_table = 'app_settings'
        verbose_name = 'App Settings'
        verbose_name_plural = 'App Settings'

    def __str__(self):
        return f"Settings (Font: {self.font_size}px)"

    @classmethod
    def get_settings(cls):
        """Get or create settings singleton."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


# ============================================================================
# INVENTORY MANAGEMENT MODELS
# ============================================================================

class KategoriBarang(models.Model):
    """Kategori untuk barang inventory (alat terapi, mainan, supplies, dll)"""
    id = models.BigAutoField(primary_key=True)
    nama_kategori = models.CharField(max_length=100, db_column='nama_kategori')
    deskripsi = models.TextField(db_column='deskripsi', null=True, blank=True)
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'kategori_barang'
        managed = True

    def __str__(self):
        return self.nama_kategori


class BarangInventory(models.Model):
    """Master data barang inventory"""
    id = models.BigAutoField(primary_key=True)
    kode_barang = models.CharField(max_length=20, db_column='kode_barang', null=True, blank=True, unique=True)
    nama_barang = models.CharField(max_length=200, db_column='nama_barang')
    kategori = models.ForeignKey(KategoriBarang, db_column='kategori_id', null=True, blank=True, on_delete=models.SET_NULL)
    satuan = models.CharField(max_length=20, db_column='satuan', help_text='pcs, box, set, dll')
    stok_minimum = models.IntegerField(db_column='stok_minimum', default=5, help_text='Alert jika stok dibawah nilai ini')
    stok_tersedia = models.IntegerField(db_column='stok_tersedia', default=0)
    harga_satuan = models.DecimalField(max_digits=12, decimal_places=2, db_column='harga_satuan', default=0, help_text='Harga per satuan')
    lokasi_penyimpanan = models.CharField(max_length=100, db_column='lokasi_penyimpanan', null=True, blank=True)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.CASCADE)
    catatan = models.TextField(db_column='catatan', null=True, blank=True)
    is_active = models.BooleanField(db_column='is_active', default=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.SET_NULL, related_name='barang_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)

    class Meta:
        db_table = 'barang_inventory'
        managed = True

    def __str__(self):
        return f"{self.kode_barang or self.id} - {self.nama_barang}"

    @property
    def is_stok_rendah(self):
        """Cek apakah stok sudah dibawah minimum"""
        return self.stok_tersedia <= self.stok_minimum

    @property
    def status_stok(self):
        """Status stok untuk display"""
        if self.stok_tersedia == 0:
            return 'HABIS'
        elif self.is_stok_rendah:
            return 'RENDAH'
        return 'AMAN'


# ============================================================================
# BACKUP SYSTEM MODELS
# ============================================================================

class BackupLog(models.Model):
    """Track database backup progress and history"""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    filename = models.CharField(max_length=255, db_column='filename')
    status = models.CharField(max_length=20, db_column='status', choices=STATUS_CHOICES, default='PENDING')
    progress = models.IntegerField(db_column='progress', default=0, help_text='Progress percentage 0-100')
    file_size = models.BigIntegerField(db_column='file_size', null=True, blank=True, help_text='Size in bytes')
    error_message = models.TextField(db_column='error_message', null=True, blank=True)
    started_at = models.DateTimeField(db_column='started_at', auto_now_add=True)
    completed_at = models.DateTimeField(db_column='completed_at', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.SET_NULL, related_name='backups_created')
    
    class Meta:
        db_table = 'backup_log'
        managed = True
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Backup {self.filename} - {self.status}"


class StokMasuk(models.Model):
    """Transaksi stok masuk (pembelian/restock)"""
    id = models.BigAutoField(primary_key=True)
    barang = models.ForeignKey(BarangInventory, db_column='barang_id', on_delete=models.CASCADE, related_name='stok_masuk_entries')
    tanggal_masuk = models.DateField(db_column='tanggal_masuk')
    jumlah = models.IntegerField(db_column='jumlah')
    harga_beli_satuan = models.DecimalField(max_digits=12, decimal_places=2, db_column='harga_beli_satuan', null=True, blank=True)
    supplier = models.CharField(max_length=200, db_column='supplier', null=True, blank=True)
    no_faktur = models.CharField(max_length=50, db_column='no_faktur', null=True, blank=True)
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.CASCADE)
    catatan = models.TextField(db_column='catatan', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.SET_NULL, related_name='stok_masuk_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta:
        db_table = 'stok_masuk'
        managed = True
        ordering = ['-tanggal_masuk', '-created_at']

    def __str__(self):
        return f"Stok Masuk {self.barang.nama_barang} - {self.jumlah} {self.barang.satuan}"

    @property
    def total_harga(self):
        """Total harga pembelian"""
        if self.harga_beli_satuan:
            return self.jumlah * self.harga_beli_satuan
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        """Override save untuk update stok barang"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Tambahkan stok ke barang
            self.barang.stok_tersedia += self.jumlah
            self.barang.save()


class PemakaianBarang(models.Model):
    """Transaksi pemakaian barang"""
    id = models.BigAutoField(primary_key=True)
    barang = models.ForeignKey(BarangInventory, db_column='barang_id', on_delete=models.CASCADE, related_name='pemakaian_entries')
    tanggal_pakai = models.DateField(db_column='tanggal_pakai')
    jumlah = models.IntegerField(db_column='jumlah')
    tujuan = models.CharField(max_length=200, db_column='tujuan', help_text='Untuk apa barang dipakai')
    registrasi = models.ForeignKey(Registrasi, db_column='registrasi_id', null=True, blank=True, on_delete=models.SET_NULL, related_name='barang_dipakai', help_text='Jika pemakaian terkait sesi terapi')
    cabang = models.ForeignKey(Cabang, db_column='cabang_id', null=True, blank=True, on_delete=models.CASCADE)
    catatan = models.TextField(db_column='catatan', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.SET_NULL, related_name='pemakaian_barang_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)

    class Meta:
        db_table = 'pemakaian_barang'
        managed = True
        ordering = ['-tanggal_pakai', '-created_at']

    def __str__(self):
        return f"Pemakaian {self.barang.nama_barang} - {self.jumlah} {self.barang.satuan}"

    @property
    def nilai_pemakaian(self):
        """Nilai pemakaian berdasarkan harga satuan barang"""
        return self.jumlah * self.barang.harga_satuan

    def save(self, *args, **kwargs):
        """Override save untuk update stok barang"""
        is_new = self.pk is None
        if is_new:
            # Validasi stok mencukupi
            if self.barang.stok_tersedia < self.jumlah:
                raise ValidationError(f'Stok {self.barang.nama_barang} tidak mencukupi. Tersedia: {self.barang.stok_tersedia}')
        
        super().save(*args, **kwargs)
        
        if is_new:
            # Kurangi stok barang
            self.barang.stok_tersedia -= self.jumlah
            self.barang.save()
