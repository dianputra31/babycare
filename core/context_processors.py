# e:/projects/python/django/teguh/babycare/core/context_processors.py
from .models import Notifikasi, AppSettings


def unread_notifikasi_count(request):
    """
    Context processor to add unread notification count to all templates
    """
    if request.user.is_authenticated:
        count = Notifikasi.objects.filter(sudah_dibaca=False).count()
        return {'unread_notifikasi_count': count}
    return {'unread_notifikasi_count': 0}

def app_settings(request):
    """
    Context processor to add app settings (font size and logo) to all templates
    """
    try:
        from .models import AppSettings
        settings = AppSettings.get_settings()
        return {
            'font_size': settings.font_size,
            'logo_url': settings.logo.url if settings.logo else None,
        }
    except Exception:
        return {
            'font_size': 14,
            'logo_url': None,
        }

def app_settings(request):
    """
    Context processor to add app settings (font size and logo) to all templates
    """
    settings = AppSettings.get_settings()
    return {
        'app_settings': settings,
        'font_size': settings.font_size,
        'logo_url': settings.logo.url if settings.logo else None,
    }
