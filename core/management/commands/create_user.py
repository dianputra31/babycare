from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Cabang, Role, UserRole


class Command(BaseCommand):
    help = 'Create a user for development. Example: python manage.py create_user --username admin --password admin123 --full-name "Admin" --email admin@example.com --cabang 1 --roles owner'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--password', type=str, default='admin123')
        parser.add_argument('--full-name', type=str, default='Admin')
        parser.add_argument('--email', type=str, default='admin@example.com')
        parser.add_argument('--cabang', type=int, default=None)
        parser.add_argument('--roles', type=str, default='')
        parser.add_argument('--force', action='store_true', help='Replace existing user if present')

    def handle(self, *args, **options):
        from django.db import connection, transaction
        from django.db.utils import OperationalError as DBOperationalError

        User = get_user_model()
        username = options['username']
        password = options['password']
        full_name = options['full_name']
        email = options['email']
        cabang_id = options['cabang']
        roles = [r.strip() for r in options['roles'].split(',') if r.strip()]
        force = options['force']

        # ensure the underlying table exists for development (SQLite fallback)
        try:
            exists = User.objects.filter(username=username).exists()
        except DBOperationalError as e:
            msg = str(e).lower()
            if 'no such table' in msg and connection.vendor == 'sqlite':
                self.stdout.write(self.style.WARNING('Detected missing table "babycare.users" in SQLite — creating minimal dev table...'))
                with connection.cursor() as cur:
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS "babycare.users" (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            password_hash varchar(128) NOT NULL,
                            last_login datetime,
                            is_superuser bool DEFAULT 0,
                            username varchar(150) NOT NULL UNIQUE,
                            full_name varchar(255),
                            email varchar(254),
                            cabang integer,
                            is_active bool DEFAULT 1,
                            created_at datetime
                        )
                    ''')
                # retry
                exists = User.objects.filter(username=username).exists()
            else:
                raise

        if exists:
            if not force:
                self.stdout.write(self.style.WARNING(f'User "{username}" already exists. Use --force to recreate.'))
                return
            else:
                User.objects.filter(username=username).delete()

        cabang_obj = None
        if cabang_id is not None:
            try:
                cabang_obj = Cabang.objects.get(pk=cabang_id)
            except Cabang.DoesNotExist:
                raise CommandError(f'Cabang with id={cabang_id} not found')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    full_name=full_name,
                    email=email,
                    cabang=cabang_obj,
                    is_active=True,
                )
        except DBOperationalError as e:
            raise CommandError(f'Failed to create user: {e}')

        # attach roles if provided
        created_roles = []
        for code in roles:
            try:
                role = Role.objects.get(code=code)
                UserRole.objects.create(user=user, role=role)
                created_roles.append(code)
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Role code "{code}" not found — skipping'))

        self.stdout.write(self.style.SUCCESS(f'User created: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        if created_roles:
            self.stdout.write(self.style.SUCCESS(f'Assigned roles: {", ".join(created_roles)}'))
