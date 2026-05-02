# e:/projects/python/django/teguh/babycare/core/context_processors.py
from django.conf import settings

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
    app_config = AppSettings.get_settings()
    return {
        'app_settings': app_config,
        'font_size': app_config.font_size,
        'app_theme': app_config.theme,
        'logo_url': app_config.logo.url if app_config.logo else None,
        'pwa_app_name': settings.PWA_APP_NAME,
        'pwa_app_description': settings.PWA_APP_DESCRIPTION,
        'pwa_theme_color': settings.PWA_THEME_COLOR,
        'pwa_background_color': settings.PWA_BACKGROUND_COLOR,
    }
