from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('login/', views.SimpleLoginView.as_view(), name='custom_login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('registrasi/', views.RegistrasiListView.as_view(), name='registrasi_list'),
    path('registrasi/new/', views.RegistrasiCreateView.as_view(), name='registrasi_create'),
    path('registrasi/<int:pk>/edit/', views.RegistrasiEditView.as_view(), name='registrasi_edit'),
    # Laporan Keuangan
    path('pemasukan/', views.PemasukanListView.as_view(), name='pemasukan_list'),
    path('pemasukan/new/', views.PemasukanCreateView.as_view(), name='pemasukan_create'),
    path('pemasukan/<int:pk>/edit/', views.PemasukanEditView.as_view(), name='pemasukan_edit'),
    path('pengeluaran/', views.PengeluaranListView.as_view(), name='pengeluaran_list'),
    path('pengeluaran/new/', views.PengeluaranCreateView.as_view(), name='pengeluaran_create'),
    path('pengeluaran/<int:pk>/edit/', views.PengeluaranEditView.as_view(), name='pengeluaran_edit'),
    # Rekap & Statistik
    path('rekap-tindakan/', views.RekapTindakanListView.as_view(), name='rekap_tindakan'),
    # Notifikasi
    path('notifikasi/', views.NotifikasiListView.as_view(), name='notifikasi_list'),
    path('notifikasi/<int:pk>/mark-read/', views.MarkNotifikasiReadView.as_view(), name='notifikasi_mark_read'),
    path('notifikasi/mark-all-read/', views.MarkAllNotifikasiReadView.as_view(), name='notifikasi_mark_all_read'),
    # Master Data
    path('cabang/', views.CabangListView.as_view(), name='cabang_list'),
    path('cabang/new/', views.CabangCreateView.as_view(), name='cabang_create'),
    path('pasien/', views.PasienListView.as_view(), name='pasien_list'),
    path('pasien/new/', views.PasienCreateView.as_view(), name='pasien_create'),
    path('terapis/', views.TerapisListView.as_view(), name='terapis_list'),
    path('terapis/new/', views.TerapisCreateView.as_view(), name='terapis_create'),
    path('jenis-terapi/', views.JenisTerapiListView.as_view(), name='jenis_terapi_list'),
    path('jenis-terapi/new/', views.JenisTerapiCreateView.as_view(), name='jenis_terapi_create'),
    # User Management
    path('user/', views.UserListView.as_view(), name='user_list'),
    path('user/new/', views.UserCreateView.as_view(), name='user_create'),
    path('user/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('user/<int:pk>/toggle-active/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),
    # AJAX Endpoints for Quick Create
    path('ajax/pasien/create/', views.AjaxCreatePasienView.as_view(), name='ajax_create_pasien'),
    path('ajax/terapis/create/', views.AjaxCreateTerapisView.as_view(), name='ajax_create_terapis'),
    path('ajax/jenis-terapi/create/', views.AjaxCreateJenisTerapiView.as_view(), name='ajax_create_jenis_terapi'),
    path('ajax/jenis-terapi/<int:jenis_terapi_id>/price/', views.AjaxGetJenisTerapiPriceView.as_view(), name='ajax_get_jenis_terapi_price'),
    path('ajax/terapis/<int:terapis_id>/transport/', views.AjaxGetTerapisTransportView.as_view(), name='ajax_get_terapis_transport'),
    path('ajax/registrasi/<int:registrasi_id>/detail/', views.AjaxGetRegistrasiDetailView.as_view(), name='ajax_get_registrasi_detail'),
    # Pembukuan (Accounting)
    path('pembukuan/total-pendapatan/', views.TotalPendapatanView.as_view(), name='total_pendapatan'),
    path('pembukuan/total-pengeluaran/', views.TotalPengeluaranView.as_view(), name='total_pengeluaran'),
    path('pembukuan/rekap-pasien-terapis/', views.RekapPasienTerapisView.as_view(), name='rekap_pasien_terapis'),
    path('pembukuan/rekap-transport-terapis/', views.RekapTransportTerapisView.as_view(), name='rekap_transport_terapis'),
    path('pembukuan/saldo-akhir/', views.SaldoAkhirView.as_view(), name='saldo_akhir'),
    # Pengaturan (Settings)
    path('pengaturan/', views.AppSettingsView.as_view(), name='app_settings'),
]
