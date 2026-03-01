from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Initialize development database with minimal RBAC tables (SQLite only)'

    def handle(self, *args, **options):
        if connection.vendor != 'sqlite':
            self.stdout.write(self.style.WARNING('This command is for SQLite development only. Skipping.'))
            return

        statements = [
            # Cabang table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.cabang" (
                id integer PRIMARY KEY AUTOINCREMENT,
                nama_cabang varchar(100) NOT NULL,
                alamat text,
                created_at datetime DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            # Users table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.users" (
                id integer PRIMARY KEY AUTOINCREMENT,
                username varchar(100) NOT NULL UNIQUE,
                password_hash text NOT NULL,
                full_name varchar(150),
                email varchar(150),
                cabang integer,
                is_active boolean DEFAULT 1,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                last_login datetime,
                is_superuser boolean DEFAULT 0
            )
            ''',
            # Roles table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.roles" (
                id integer PRIMARY KEY AUTOINCREMENT,
                nama_role varchar(50) NOT NULL,
                deskripsi text
            )
            ''',
            # Permissions table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.permissions" (
                id integer PRIMARY KEY AUTOINCREMENT,
                module varchar(100) NOT NULL,
                action varchar(50) NOT NULL,
                code varchar(150) NOT NULL UNIQUE
            )
            ''',
            # UserRole table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.user_roles" (
                id integer PRIMARY KEY AUTOINCREMENT,
                user_id integer NOT NULL,
                role_id integer NOT NULL
            )
            ''',
            # RolePermission table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.role_permissions" (
                id integer PRIMARY KEY AUTOINCREMENT,
                role_id integer NOT NULL,
                permission_id integer NOT NULL
            )
            ''',
            # Pasien table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.pasien" (
                id integer PRIMARY KEY AUTOINCREMENT,
                kode_pasien varchar(20) UNIQUE,
                nama_anak varchar(150) NOT NULL,
                tanggal_lahir date NOT NULL,
                jenis_kelamin varchar(1),
                nama_orang_tua varchar(150),
                alamat text,
                no_wa varchar(20),
                cabang_id integer,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime DEFAULT CURRENT_TIMESTAMP,
                is_deleted boolean DEFAULT 0
            )
            ''',
            # JenisTerapi table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.jenis_terapi" (
                id integer PRIMARY KEY AUTOINCREMENT,
                nama_terapi varchar(150) NOT NULL,
                kategori_usia_min integer,
                kategori_usia_max integer,
                harga numeric(12, 2) DEFAULT 0.00,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime DEFAULT CURRENT_TIMESTAMP,
                is_deleted boolean DEFAULT 0
            )
            ''',
            # Terapis table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.terapis" (
                id integer PRIMARY KEY AUTOINCREMENT,
                nama_terapis varchar(150) NOT NULL,
                no_hp varchar(20),
                alamat text,
                cabang_id integer,
                biaya_transport_default numeric(10, 2) DEFAULT 0.00,
                is_active boolean DEFAULT 1,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime DEFAULT CURRENT_TIMESTAMP,
                is_deleted boolean DEFAULT 0
            )
            ''',
            # Registrasi table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.registrasi" (
                id integer PRIMARY KEY AUTOINCREMENT,
                kode_registrasi varchar(30) UNIQUE,
                pasien_id integer NOT NULL,
                jenis_terapi_id integer NOT NULL,
                terapis_id integer,
                tanggal_kunjungan date NOT NULL,
                harga numeric(12, 2) NOT NULL,
                biaya_transport numeric(10, 2) DEFAULT 0.00,
                total_bayar numeric(14, 2) DEFAULT 0.00,
                status varchar(20) DEFAULT 'pending',
                catatan text,
                cabang_id integer,
                created_by integer,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                updated_at datetime DEFAULT CURRENT_TIMESTAMP,
                is_deleted boolean DEFAULT 0
            )
            ''',
            # Pemasukan table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.pemasukan" (
                id integer PRIMARY KEY AUTOINCREMENT,
                registrasi_id integer,
                jumlah numeric(14, 2) NOT NULL,
                metode_pembayaran varchar(20),
                keterangan text,
                created_by integer,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                cabang_id integer
            )
            ''',
            # Pengeluaran table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.pengeluaran" (
                id integer PRIMARY KEY AUTOINCREMENT,
                jumlah numeric(14, 2) NOT NULL,
                kategori varchar(50),
                keterangan text,
                created_at datetime DEFAULT CURRENT_TIMESTAMP,
                cabang_id integer
            )
            ''',
            # TransportTerapis table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.transport_terapis" (
                id integer PRIMARY KEY AUTOINCREMENT,
                terapis_id integer NOT NULL,
                tanggal date NOT NULL,
                biaya numeric(10, 2) NOT NULL
            )
            ''',
            # Notifikasi table
            '''
            CREATE TABLE IF NOT EXISTS "babycare.notifikasi" (
                id integer PRIMARY KEY AUTOINCREMENT,
                cabang_id integer,
                title varchar(255) NOT NULL,
                message text NOT NULL,
                is_read boolean DEFAULT 0,
                meta json,
                created_at datetime DEFAULT CURRENT_TIMESTAMP
            )
            ''',
        ]

        with connection.cursor() as cursor:
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                    self.stdout.write(self.style.SUCCESS(f'✓ Created/verified table'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'✗ Error: {e}'))

        self.stdout.write(self.style.SUCCESS('✓ Development database initialized'))
