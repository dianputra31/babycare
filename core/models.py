# e:/projects/python/django/teguh/babycare/core/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from decimal import Decimal
from .services.registration_service import calculate_total_bayar

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

    def get_permissions(self):
        return Permission.objects.filter(rolepermission__role__userrole__user=self).distinct()

    def has_permission(self, code: str) -> bool:
        if not self.is_authenticated:
            return False
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
    status = models.CharField(max_length=20, db_column='status', default='BOOKED')
    harga = models.DecimalField(db_column='harga', max_digits=12, decimal_places=2)
    biaya_transport = models.DecimalField(db_column='biaya_transport', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_bayar = models.DecimalField(db_column='total_bayar', max_digits=12, decimal_places=2, null=True, blank=True)
    catatan = models.TextField(db_column='catatan', null=True, blank=True)
    created_by = models.ForeignKey(User, db_column='created_by', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='registrasi_created')
    created_at = models.DateTimeField(db_column='created_at', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', auto_now=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)

    class Meta:
        db_table = 'registrasi'
        managed = False

    def __str__(self):
        return f"Registrasi #{self.id} - {self.pasien}"

    def save(self, *args, **kwargs):
        self.total_bayar = calculate_total_bayar(self.harga, self.biaya_transport)
        super().save(*args, **kwargs)

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

    class Meta:
        db_table = 'pengeluaran'
        managed = False

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


class AppSettings(models.Model):
    """Global application settings like font size and logo."""
    id = models.AutoField(primary_key=True)
    font_size = models.IntegerField(default=14, help_text='Font size in pixels (default: 14)')
    logo = models.ImageField(upload_to='logos/', null=True, blank=True, help_text='Upload logo image')
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
