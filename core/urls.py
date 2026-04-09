from django.urls import path
from . import views
from . import views_inventory

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('manifest.json', views.manifest_json, name='manifest_json'),
    path('sw.js', views.service_worker, name='service_worker'),
    path('offline/', views.offline_view, name='offline'),
    path('login/', views.SimpleLoginView.as_view(), name='custom_login'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('registrasi/', views.RegistrasiListView.as_view(), name='registrasi_list'),
    path('registrasi/new/', views.RegistrasiCreateView.as_view(), name='registrasi_create'),
    path('registrasi/<int:pk>/edit/', views.RegistrasiEditView.as_view(), name='registrasi_edit'),
    path('registrasi/<int:registrasi_id>/send-whatsapp/', views.send_whatsapp_reminder, name='send_whatsapp_reminder'),
    path('registrasi/<int:registrasi_id>/progress/add/', views.add_progress_tracking, name='add_progress_tracking'),
    path('registrasi/export/excel/', views.export_registrasi_excel, name='export_registrasi_excel'),
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
    path('notifikasi/generate/manual/', views.GenerateNotificationsManualView.as_view(), name='generate_notifications_manual'),
    path('template-pesan/', views.TemplatePesanListView.as_view(), name='template_pesan_list'),
    path('template-pesan/new/', views.TemplatePesanCreateView.as_view(), name='template_pesan_create'),
    path('template-pesan/<int:pk>/edit/', views.TemplatePesanEditView.as_view(), name='template_pesan_edit'),
    path('template-pesan/<int:pk>/delete/', views.TemplatePesanDeleteView.as_view(), name='template_pesan_delete'),
    # Master Data
    path('cabang/', views.CabangListView.as_view(), name='cabang_list'),
    path('cabang/new/', views.CabangCreateView.as_view(), name='cabang_create'),
    path('cabang/<int:pk>/edit/', views.CabangUpdateView.as_view(), name='cabang_edit'),
    path('cabang/<int:pk>/delete/', views.CabangDeleteView.as_view(), name='cabang_delete'),
    path('pasien/', views.PasienListView.as_view(), name='pasien_list'),
    path('pasien/new/', views.PasienCreateView.as_view(), name='pasien_create'),
    path('pasien/<int:pk>/edit/', views.PasienEditView.as_view(), name='pasien_edit'),
    path('pasien/export/excel/', views.export_pasien_excel, name='export_pasien_excel'),
    path('pasien/import/', views.ImportPasienView.as_view(), name='import_pasien'),
    path('terapis/', views.TerapisListView.as_view(), name='terapis_list'),
    path('terapis/new/', views.TerapisCreateView.as_view(), name='terapis_create'),
    path('terapis/<int:pk>/edit/', views.TerapisUpdateView.as_view(), name='terapis_edit'),
    path('terapis/<int:pk>/delete/', views.TerapisDeleteView.as_view(), name='terapis_delete'),
    path('jenis-terapi/', views.JenisTerapiListView.as_view(), name='jenis_terapi_list'),
    path('jenis-terapi/new/', views.JenisTerapiCreateView.as_view(), name='jenis_terapi_create'),
    path('jenis-terapi/<int:pk>/edit/', views.JenisTerapiUpdateView.as_view(), name='jenis_terapi_edit'),
    path('jenis-terapi/<int:pk>/delete/', views.JenisTerapiDeleteView.as_view(), name='jenis_terapi_delete'),
    # User Management
    path('user/', views.UserListView.as_view(), name='user_list'),
    path('user/new/', views.UserCreateView.as_view(), name='user_create'),
    path('user/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('user/<int:pk>/toggle-active/', views.UserToggleActiveView.as_view(), name='user_toggle_active'),
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/new/', views.RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/edit/', views.RoleEditView.as_view(), name='role_edit'),
    path('roles/seed-defaults/', views.RoleSeedDefaultsView.as_view(), name='role_seed_defaults'),
    path('akun/password/', views.ChangeOwnPasswordView.as_view(), name='change_own_password'),
    # AJAX Endpoints for Quick Create
    path('ajax/pasien/create/', views.AjaxCreatePasienView.as_view(), name='ajax_create_pasien'),
    path('ajax/terapis/create/', views.AjaxCreateTerapisView.as_view(), name='ajax_create_terapis'),
    path('ajax/jenis-terapi/create/', views.AjaxCreateJenisTerapiView.as_view(), name='ajax_create_jenis_terapi'),
    path('ajax/jenis-terapi/<int:jenis_terapi_id>/price/', views.AjaxGetJenisTerapiPriceView.as_view(), name='ajax_get_jenis_terapi_price'),
    # API for Multi-Therapy
    path('api/jenis-terapi/<int:pk>/', views.api_jenis_terapi_detail, name='api_jenis_terapi_detail'),
    path('ajax/terapis/<int:terapis_id>/transport/', views.AjaxGetTerapisTransportView.as_view(), name='ajax_get_terapis_transport'),
    path('ajax/registrasi/<int:registrasi_id>/detail/', views.AjaxGetRegistrasiDetailView.as_view(), name='ajax_get_registrasi_detail'),
    # Calendar View
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('api/calendar/events/', views.calendar_events_api, name='calendar_events_api'),
    path('api/registrasi/<int:registrasi_id>/update-date/', views.update_registrasi_date_api, name='update_registrasi_date_api'),
    # Pembukuan (Accounting)
    path('pembukuan/total-pendapatan/', views.TotalPendapatanView.as_view(), name='total_pendapatan'),
    path('pembukuan/total-pengeluaran/', views.TotalPengeluaranView.as_view(), name='total_pengeluaran'),
    path('pembukuan/rekap-pasien-terapis/', views.RekapPasienTerapisView.as_view(), name='rekap_pasien_terapis'),
    path('pembukuan/rekap-transport-terapis/', views.RekapTransportTerapisView.as_view(), name='rekap_transport_terapis'),
    path('pembukuan/saldo-akhir/', views.SaldoAkhirView.as_view(), name='saldo_akhir'),
    # Pengaturan (Settings)
    path('pengaturan/', views.AppSettingsView.as_view(), name='app_settings'),
    # Notification Generation
    path('notifikasi/generate/', views.GenerateNotificationsView.as_view(), name='generate_notifications'),
    
    # ============================================================================
    # INVENTORY MANAGEMENT
    # ============================================================================
    # Kategori Barang
    path('inventory/kategori/', views_inventory.KategoriBarangListView.as_view(), name='kategori_barang_list'),
    path('inventory/kategori/new/', views_inventory.KategoriBarangCreateView.as_view(), name='kategori_barang_create'),
    path('inventory/kategori/<int:pk>/edit/', views_inventory.KategoriBarangUpdateView.as_view(), name='kategori_barang_edit'),
    # Master Barang
    path('inventory/barang/', views_inventory.BarangInventoryListView.as_view(), name='barang_inventory_list'),
    path('inventory/barang/new/', views_inventory.BarangInventoryCreateView.as_view(), name='barang_inventory_create'),
    path('inventory/barang/<int:pk>/edit/', views_inventory.BarangInventoryUpdateView.as_view(), name='barang_inventory_edit'),
    # Stok Masuk
    path('inventory/stok-masuk/', views_inventory.StokMasukListView.as_view(), name='stok_masuk_list'),
    path('inventory/stok-masuk/new/', views_inventory.StokMasukCreateView.as_view(), name='stok_masuk_create'),
    # Pemakaian Barang
    path('inventory/pemakaian/', views_inventory.PemakaianBarangListView.as_view(), name='pemakaian_barang_list'),
    path('inventory/pemakaian/new/', views_inventory.PemakaianBarangCreateView.as_view(), name='pemakaian_barang_create'),
    # Laporan Inventory
    path('inventory/laporan/', views_inventory.LaporanInventoryView.as_view(), name='laporan_inventory'),
]
