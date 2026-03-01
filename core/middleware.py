from django.utils.deprecation import MiddlewareMixin
from django.db import OperationalError


class RBACMiddleware(MiddlewareMixin):
    """Inject user roles & permissions into request and expose cabang filter helper.

    - request.user_roles -> set of role codes (lowercased)
    - request.user_permissions -> set of permission codes
    - request.cabang_id -> None for owner (means all), or cabang id for admin/other
    - request.filter_by_cabang(qs) -> helper to filter querysets by cabang
    """

    def process_request(self, request):
        user = getattr(request, 'user', None)
        request.user_roles = set()
        request.user_permissions = set()
        request.cabang_id = None

        if user and user.is_authenticated:
            try:
                from .models import Role, Permission
                roles = Role.objects.filter(userrole__user=user)
                request.user_roles = set(r.nama_role.lower() for r in roles)
                perms = Permission.objects.filter(rolepermission__role__in=roles).values_list('code', flat=True)
                request.user_permissions = set(p for p in perms if p)

                # determine cabang scoping
                if 'owner' in request.user_roles:
                    request.cabang_id = None  # owner sees all
                else:
                    # admin and others limited to their cabang
                    request.cabang_id = getattr(user.cabang, 'id', None)
            except (OperationalError, Exception):
                # Tables may not exist or user has no roles during development
                pass

        def _filter_by_cabang(qs):
            if request.cabang_id is None:
                return qs
            # assume model has `cabang_id` or `cabang` FK
            try:
                return qs.filter(cabang_id=request.cabang_id)
            except Exception:
                return qs

        request.filter_by_cabang = _filter_by_cabang
