import inspect
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


def permission_required(code):
    """Decorator to require a custom permission code from RBAC tables.

    Usage:
      @permission_required('pasien_create')        # function view
      @method_decorator(permission_required('x'), name='dispatch')  # CBV
    """
    def _decorator(view):
        # If decorating a class-based view class, wrap its dispatch method
        if inspect.isclass(view):
            view.dispatch = method_decorator(_decorator)(view.dispatch)
            return view

        @wraps(view)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                # defer to login_required behaviour
                return login_required(view)(request, *args, **kwargs)
            # request.user.has_permission is defined on the custom User model
            if not getattr(request.user, 'has_permission', lambda c: False)(code):
                raise PermissionDenied(f"Missing permission: {code}")
            return view(request, *args, **kwargs)

        return _wrapped

    return _decorator
