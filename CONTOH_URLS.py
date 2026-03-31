"""
Update URL Configuration untuk Multi-Terapi
Tambahkan URL patterns ini ke core/urls.py
"""

from django.urls import path
from . import views

# Tambahkan URL patterns berikut:

urlpatterns = [
    # ... existing URLs ...
    
    # API Endpoint untuk AJAX - Get Harga Terapi
    path('api/jenis-terapi/<int:pk>/', views.api_jenis_terapi_detail, name='api_jenis_terapi_detail'),
    
    # Jika menggunakan view baru untuk multi-terapi:
    # Option 1: Ganti view lama dengan view baru
    path('registrasi/tambah/', views.RegistrasiCreateViewMultiTerapi.as_view(), name='registrasi_create'),
    path('registrasi/<int:pk>/edit/', views.RegistrasiEditViewMultiTerapi.as_view(), name='registrasi_edit'),
    
    # Option 2: Atau buat URL baru dan keep yang lama untuk backward compatibility
    # path('registrasi/tambah-multi/', views.RegistrasiCreateViewMultiTerapi.as_view(), name='registrasi_create_multi'),
    # path('registrasi/<int:pk>/edit-multi/', views.RegistrasiEditViewMultiTerapi.as_view(), name='registrasi_edit_multi'),
    
    # ... existing URLs ...
]

# ========================================
# Contoh URL patterns lengkap (referensi):
# ========================================

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Registrasi
    path('registrasi/', views.RegistrasiListView.as_view(), name='registrasi_list'),
    path('registrasi/tambah/', views.RegistrasiCreateViewMultiTerapi.as_view(), name='registrasi_create'),
    path('registrasi/<int:pk>/edit/', views.RegistrasiEditViewMultiTerapi.as_view(), name='registrasi_edit'),
    path('registrasi/<int:pk>/delete/', views.registrasi_delete, name='registrasi_delete'),
    
    # API Endpoints
    path('api/jenis-terapi/<int:pk>/', views.api_jenis_terapi_detail, name='api_jenis_terapi_detail'),
    
    # Pasien
    path('pasien/', views.PasienListView.as_view(), name='pasien_list'),
    path('pasien/tambah/', views.PasienCreateView.as_view(), name='pasien_create'),
    path('pasien/<int:pk>/edit/', views.PasienEditView.as_view(), name='pasien_edit'),
    
    # Terapis
    path('terapis/', views.TerapisListView.as_view(), name='terapis_list'),
    path('terapis/tambah/', views.TerapisCreateView.as_view(), name='terapis_create'),
    path('terapis/<int:pk>/edit/', views.TerapisEditView.as_view(), name='terapis_edit'),
    
    # Jenis Terapi
    path('jenis-terapi/', views.JenisTerapiListView.as_view(), name='jenis_terapi_list'),
    path('jenis-terapi/tambah/', views.JenisTerapiCreateView.as_view(), name='jenis_terapi_create'),
    path('jenis-terapi/<int:pk>/edit/', views.JenisTerapiEditView.as_view(), name='jenis_terapi_edit'),
    
    # Pemasukan & Pengeluaran
    path('pemasukan/', views.PemasukanListView.as_view(), name='pemasukan_list'),
    path('pemasukan/tambah/', views.PemasukanCreateView.as_view(), name='pemasukan_create'),
    path('pengeluaran/', views.PengeluaranListView.as_view(), name='pengeluaran_list'),
    path('pengeluaran/tambah/', views.PengeluaranCreateView.as_view(), name='pengeluaran_create'),
    
    # Notifikasi
    path('notifikasi/', views.NotifikasiListView.as_view(), name='notifikasi_list'),
    
    # Settings
    path('pengaturan/', views.pengaturan_view, name='pengaturan'),
]
