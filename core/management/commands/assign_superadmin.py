from django.core.management.base import BaseCommand, CommandError

from core.models import Role, User
from core.rbac import replace_user_roles, seed_default_roles


class Command(BaseCommand):
    help = 'Seed default RBAC roles and assign the superadmin role to a user.'

    def add_arguments(self, parser):
        parser.add_argument('username', help='Username that should receive the superadmin role.')

    def handle(self, *args, **options):
        username = (options['username'] or '').strip()
        if not username:
            raise CommandError('Username wajib diisi.')

        seed_default_roles()

        user = User.objects.filter(username__iexact=username).first()
        if user is None:
            raise CommandError(f'User dengan username {username} tidak ditemukan.')

        superadmin_role = Role.objects.filter(nama_role__iexact='superadmin').first()
        if superadmin_role is None:
            raise CommandError('Role superadmin tidak ditemukan setelah proses seed.')

        existing_roles = list(user.get_roles())
        existing_role_ids = {role.pk for role in existing_roles}
        if superadmin_role.pk not in existing_role_ids:
            existing_roles.append(superadmin_role)

        replace_user_roles(user, existing_roles)

        self.stdout.write(self.style.SUCCESS(
            f'User {user.username} sekarang memiliki role: {", ".join(role.nama_role for role in existing_roles)}'
        ))