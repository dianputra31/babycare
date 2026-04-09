from django.db import transaction
from django.db import connection
from django.db.models import Q

from .models import Permission, Role, RolePermission, User, UserRole


RESERVED_SUPERADMIN_ROLES = {'superadmin', 'owner'}

PERMISSION_GROUPS = [
    {
        'key': 'dashboard',
        'label': 'Dashboard',
        'permissions': [
            {'action': 'view', 'code': 'dashboard_view', 'label': 'Lihat dashboard dan ringkasan utama'},
        ],
    },
    {
        'key': 'notifikasi',
        'label': 'Notifikasi',
        'permissions': [
            {'action': 'view', 'code': 'notifikasi_view', 'label': 'Lihat daftar notifikasi'},
            {'action': 'generate', 'code': 'notifikasi_generate', 'label': 'Generate dan refresh notifikasi'},
            {'action': 'mark_read', 'code': 'notifikasi_mark_read', 'label': 'Tandai notifikasi sudah dibaca'},
            {'action': 'template_view', 'code': 'template_pesan_view', 'label': 'Lihat menu template pesan'},
            {'action': 'template_edit', 'code': 'template_pesan_edit', 'label': 'Tambah, ubah, dan hapus template pesan'},
        ],
    },
    {
        'key': 'registrasi',
        'label': 'Registrasi & Appointment',
        'permissions': [
            {'action': 'view', 'code': 'registrasi_view', 'label': 'Lihat daftar registrasi'},
            {'action': 'create', 'code': 'registrasi_create', 'label': 'Tambah registrasi baru'},
            {'action': 'edit', 'code': 'registrasi_edit', 'label': 'Ubah data registrasi'},
            {'action': 'export', 'code': 'registrasi_export', 'label': 'Export data registrasi'},
            {'action': 'reschedule', 'code': 'registrasi_reschedule', 'label': 'Geser jadwal via kalender'},
            {'action': 'send_whatsapp', 'code': 'registrasi_send_whatsapp', 'label': 'Kirim reminder WhatsApp'},
            {'action': 'add_progress', 'code': 'registrasi_add_progress', 'label': 'Tambah progress terapi'},
        ],
    },
    {
        'key': 'calendar',
        'label': 'Kalender',
        'permissions': [
            {'action': 'view', 'code': 'calendar_view', 'label': 'Lihat kalender appointment'},
        ],
    },
    {
        'key': 'pasien',
        'label': 'Pasien',
        'permissions': [
            {'action': 'view', 'code': 'pasien_view', 'label': 'Lihat data pasien'},
            {'action': 'create', 'code': 'pasien_create', 'label': 'Tambah pasien'},
            {'action': 'edit', 'code': 'pasien_edit', 'label': 'Ubah data pasien'},
            {'action': 'export', 'code': 'pasien_export', 'label': 'Export data pasien'},
        ],
    },
    {
        'key': 'terapis',
        'label': 'Terapis',
        'permissions': [
            {'action': 'view', 'code': 'terapis_view', 'label': 'Lihat data terapis'},
            {'action': 'create', 'code': 'terapis_create', 'label': 'Tambah terapis'},
            {'action': 'edit', 'code': 'terapis_edit', 'label': 'Ubah data terapis'},
            {'action': 'delete', 'code': 'terapis_delete', 'label': 'Hapus/nonaktifkan terapis'},
        ],
    },
    {
        'key': 'jenis_terapi',
        'label': 'Jenis Terapi',
        'permissions': [
            {'action': 'view', 'code': 'jenis_terapi_view', 'label': 'Lihat master jenis terapi'},
            {'action': 'create', 'code': 'jenis_terapi_create', 'label': 'Tambah jenis terapi'},
            {'action': 'edit', 'code': 'jenis_terapi_edit', 'label': 'Ubah jenis terapi'},
            {'action': 'delete', 'code': 'jenis_terapi_delete', 'label': 'Hapus/nonaktifkan jenis terapi'},
        ],
    },
    {
        'key': 'cabang',
        'label': 'Cabang',
        'permissions': [
            {'action': 'view', 'code': 'cabang_view', 'label': 'Lihat data cabang'},
            {'action': 'create', 'code': 'cabang_create', 'label': 'Tambah cabang'},
            {'action': 'edit', 'code': 'cabang_edit', 'label': 'Ubah data cabang'},
            {'action': 'delete', 'code': 'cabang_delete', 'label': 'Hapus/nonaktifkan cabang'},
        ],
    },
    {
        'key': 'keuangan',
        'label': 'Keuangan',
        'permissions': [
            {'action': 'pemasukan_view', 'code': 'pemasukan_view', 'label': 'Lihat pemasukan'},
            {'action': 'pemasukan_create', 'code': 'pemasukan_create', 'label': 'Tambah pemasukan'},
            {'action': 'pemasukan_edit', 'code': 'pemasukan_edit', 'label': 'Ubah pemasukan'},
            {'action': 'pengeluaran_view', 'code': 'pengeluaran_view', 'label': 'Lihat pengeluaran'},
            {'action': 'pengeluaran_create', 'code': 'pengeluaran_create', 'label': 'Tambah pengeluaran'},
            {'action': 'pengeluaran_edit', 'code': 'pengeluaran_edit', 'label': 'Ubah pengeluaran'},
        ],
    },
    {
        'key': 'inventory',
        'label': 'Inventory',
        'permissions': [
            {'action': 'kategori_view', 'code': 'kategori_barang_view', 'label': 'Lihat kategori barang'},
            {'action': 'kategori_create', 'code': 'kategori_barang_create', 'label': 'Tambah kategori barang'},
            {'action': 'kategori_edit', 'code': 'kategori_barang_edit', 'label': 'Ubah kategori barang'},
            {'action': 'kategori_delete', 'code': 'kategori_barang_delete', 'label': 'Hapus kategori barang'},
            
            {'action': 'barang_view', 'code': 'barang_inventory_view', 'label': 'Lihat data barang inventory'},
            {'action': 'barang_create', 'code': 'barang_inventory_create', 'label': 'Tambah barang inventory'},
            {'action': 'barang_edit', 'code': 'barang_inventory_edit', 'label': 'Ubah data barang inventory'},
            {'action': 'barang_delete', 'code': 'barang_inventory_delete', 'label': 'Hapus barang inventory'},
            
            {'action': 'stok_masuk_view', 'code': 'stok_masuk_view', 'label': 'Lihat stok masuk'},
            {'action': 'stok_masuk_create', 'code': 'stok_masuk_create', 'label': 'Tambah stok masuk'},
            {'action': 'stok_masuk_edit', 'code': 'stok_masuk_edit', 'label': 'Ubah stok masuk'},
            {'action': 'stok_masuk_delete', 'code': 'stok_masuk_delete', 'label': 'Hapus stok masuk'},
            
            {'action': 'pemakaian_view', 'code': 'pemakaian_barang_view', 'label': 'Lihat pemakaian barang'},
            {'action': 'pemakaian_create', 'code': 'pemakaian_barang_create', 'label': 'Tambah pemakaian barang'},
            {'action': 'pemakaian_edit', 'code': 'pemakaian_barang_edit', 'label': 'Ubah pemakaian barang'},
            {'action': 'pemakaian_delete', 'code': 'pemakaian_barang_delete', 'label': 'Hapus pemakaian barang'},
            
            {'action': 'stok_opname_view', 'code': 'stok_opname_view', 'label': 'Lihat stok opname'},
            {'action': 'stok_opname_create', 'code': 'stok_opname_create', 'label': 'Lakukan stok opname'},
        ],
    },
    {
        'key': 'laporan',
        'label': 'Laporan & Pembukuan',
        'permissions': [
            {'action': 'rekap_view', 'code': 'rekap_view', 'label': 'Lihat rekap tindakan'},
            {'action': 'pembukuan_view', 'code': 'pembukuan_view', 'label': 'Lihat seluruh halaman pembukuan'},
        ],
    },
    {
        'key': 'users',
        'label': 'User Management',
        'permissions': [
            {'action': 'view', 'code': 'user_view', 'label': 'Lihat daftar user'},
            {'action': 'create', 'code': 'user_create', 'label': 'Tambah user'},
            {'action': 'edit', 'code': 'user_edit', 'label': 'Ubah user dan role'},
            {'action': 'toggle_active', 'code': 'user_toggle_active', 'label': 'Aktif/nonaktifkan user'},
        ],
    },
    {
        'key': 'roles',
        'label': 'Role & Privileges',
        'permissions': [
            {'action': 'view', 'code': 'role_view', 'label': 'Lihat menu role & privileges'},
            {'action': 'create', 'code': 'role_create', 'label': 'Buat role baru'},
            {'action': 'edit', 'code': 'role_edit', 'label': 'Ubah role dan privilege'},
            {'action': 'seed_defaults', 'code': 'role_seed_defaults', 'label': 'Isi role rekomendasi bawaan'},
        ],
    },
    {
        'key': 'settings',
        'label': 'Pengaturan',
        'permissions': [
            {'action': 'view', 'code': 'settings_view', 'label': 'Lihat halaman pengaturan'},
            {'action': 'edit', 'code': 'settings_edit', 'label': 'Ubah pengaturan aplikasi'},
        ],
    },
]

DEFAULT_ROLE_BLUEPRINTS = [
    {
        'name': 'superadmin',
        'description': 'Akses penuh semua modul, semua cabang, termasuk atur role dan privilege.',
        'summary': 'Pemilik sistem atau admin pusat. Tidak dibatasi cabang.',
        'full_access': True,
        'permissions': [],
    },
    {
        'name': 'admin operasional',
        'description': 'Fokus ke operasional harian: registrasi, pasien, jadwal, notifikasi, dan master data dasar.',
        'summary': 'Cocok untuk kepala operasional cabang.',
        'full_access': False,
        'permissions': [
            'dashboard_view', 'notifikasi_view', 'notifikasi_generate', 'notifikasi_mark_read', 'template_pesan_view', 'template_pesan_edit',
            'registrasi_view', 'registrasi_create', 'registrasi_edit', 'registrasi_reschedule', 'registrasi_send_whatsapp', 'registrasi_add_progress',
            'calendar_view',
            'pasien_view', 'pasien_create', 'pasien_edit',
            'terapis_view', 'terapis_create', 'terapis_edit',
            'jenis_terapi_view', 'jenis_terapi_create', 'jenis_terapi_edit',
            # Inventory permissions
            'kategori_barang_view', 'kategori_barang_create', 'kategori_barang_edit',
            'barang_inventory_view', 'barang_inventory_create', 'barang_inventory_edit',
            'stok_masuk_view', 'stok_masuk_create', 'stok_masuk_edit',
            'pemakaian_barang_view', 'pemakaian_barang_create', 'pemakaian_barang_edit',
            'stok_opname_view', 'stok_opname_create',
        ],
    },
    {
        'name': 'front office',
        'description': 'Menangani pendaftaran, follow-up pasien, dan pengelolaan jadwal tanpa akses ke pengaturan sensitif.',
        'summary': 'Cocok untuk admin resepsionis atau CS.',
        'full_access': False,
        'permissions': [
            'dashboard_view', 'notifikasi_view', 'notifikasi_mark_read', 'template_pesan_view', 'template_pesan_edit',
            'registrasi_view', 'registrasi_create', 'registrasi_edit', 'registrasi_send_whatsapp',
            'calendar_view',
            'pasien_view', 'pasien_create', 'pasien_edit',
            'terapis_view', 'jenis_terapi_view',
        ],
    },
    {
        'name': 'finance',
        'description': 'Khusus area keuangan dan laporan, tanpa hak ubah struktur user atau privilege.',
        'summary': 'Cocok untuk kasir atau admin keuangan.',
        'full_access': False,
        'permissions': [
            'dashboard_view', 'pemasukan_view', 'pemasukan_create', 'pemasukan_edit',
            'pengeluaran_view', 'pengeluaran_create', 'pengeluaran_edit',
            'rekap_view', 'pembukuan_view', 'notifikasi_view',
            # Inventory permissions (finance usually manages purchasing)
            'kategori_barang_view', 'barang_inventory_view',
            'stok_masuk_view', 'stok_masuk_create', 'stok_masuk_edit',
            'pemakaian_barang_view', 'stok_opname_view',
        ],
    },
    {
        'name': 'terapis',
        'description': 'Akses ringan untuk melihat jadwal, pasien, dan menambah catatan progress terapi.',
        'summary': 'Cocok untuk tenaga terapis lapangan.',
        'full_access': False,
        'permissions': [
            'dashboard_view', 'registrasi_view', 'registrasi_add_progress', 'calendar_view',
            'pasien_view', 'notifikasi_view', 'notifikasi_mark_read',
        ],
    },
    {
        'name': 'viewer',
        'description': 'Hanya baca. Bisa dipakai untuk owner pasif, auditor, atau observer.',
        'summary': 'Tidak bisa mengubah transaksi atau master data.',
        'full_access': False,
        'permissions': [
            'dashboard_view', 'registrasi_view', 'pasien_view', 'terapis_view', 'jenis_terapi_view',
            'notifikasi_view', 'template_pesan_view', 'rekap_view', 'pembukuan_view',
            # Inventory view-only
            'kategori_barang_view', 'barang_inventory_view', 'stok_masuk_view', 
            'pemakaian_barang_view', 'stok_opname_view',
        ],
    },
]


def normalize_role_name(name):
    return ' '.join((name or '').strip().lower().split())


def sync_permission_catalog():
    created = 0
    updated = 0

    for group in PERMISSION_GROUPS:
        for item in group['permissions']:
            permission, was_created = Permission.objects.get_or_create(
                code=item['code'],
                defaults={
                    'module': group['label'],
                    'action': item['action'],
                },
            )
            if was_created:
                created += 1
                continue

            changed = False
            if permission.module != group['label']:
                permission.module = group['label']
                changed = True
            if permission.action != item['action']:
                permission.action = item['action']
                changed = True
            if changed:
                permission.save(update_fields=['module', 'action'])
                updated += 1

    return {'created': created, 'updated': updated}


def replace_role_permissions(role, permissions):
    permission_ids = [getattr(permission, 'pk', permission) for permission in permissions]
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM role_permissions WHERE role_id = %s', [role.pk])
        if permission_ids:
            cursor.executemany(
                'INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)',
                [(role.pk, permission_id) for permission_id in permission_ids],
            )


def replace_user_roles(user, roles):
    role_ids = [getattr(role, 'pk', role) for role in roles]
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM user_roles WHERE user_id = %s', [user.pk])
        if role_ids:
            cursor.executemany(
                'INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)',
                [(user.pk, role_id) for role_id in role_ids],
            )

def get_permission_groups_for_display():
    sync_permission_catalog()
    permissions_by_code = {
        permission.code: permission
        for permission in Permission.objects.all().order_by('module', 'action', 'code')
    }
    groups = []
    for group in PERMISSION_GROUPS:
        group_permissions = []
        for item in group['permissions']:
            permission = permissions_by_code.get(item['code'])
            if permission is None:
                continue
            group_permissions.append({
                'id': permission.id,
                'code': permission.code,
                'label': item['label'],
                'action': item['action'],
            })
        groups.append({
            'key': group['key'],
            'label': group['label'],
            'permissions': group_permissions,
        })
    return groups


def is_rbac_bootstrap_mode():
    if User.objects.filter(is_superuser=True).exists():
        return False
    return not UserRole.objects.filter(
        Q(role__nama_role__iexact='superadmin') | Q(role__nama_role__iexact='owner')
    ).exists()


def can_manage_roles(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superadmin_role', False):
        return True
    return is_rbac_bootstrap_mode()


@transaction.atomic
def seed_default_roles():
    sync_permission_catalog()
    permissions_by_code = {
        permission.code: permission
        for permission in Permission.objects.all()
    }
    created = []
    updated = []

    for blueprint in DEFAULT_ROLE_BLUEPRINTS:
        role = Role.objects.filter(nama_role__iexact=blueprint['name']).first()
        was_created = role is None
        if was_created:
            role = Role(nama_role=blueprint['name'], deskripsi=blueprint['description'])
        else:
            role.deskripsi = blueprint['description']

        role.save()

        RolePermission.objects.filter(role=role).delete()
        if blueprint['full_access']:
            selected_permissions = list(permissions_by_code.values())
        else:
            selected_permissions = [
                permissions_by_code[code]
                for code in blueprint['permissions']
                if code in permissions_by_code
            ]

        replace_role_permissions(role, selected_permissions)

        if was_created:
            created.append(role.nama_role)
        else:
            updated.append(role.nama_role)

    return {'created': created, 'updated': updated}