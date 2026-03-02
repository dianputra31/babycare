# Generated migration - simplified to avoid managed=False table issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_updated_by_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsettings',
            name='birthday_notif_days_before',
            field=models.IntegerField(default=1, help_text='Hari sebelum ulang tahun untuk notifikasi (1=H-1, 2=H-2)'),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='enable_birthday_notif',
            field=models.BooleanField(default=True, help_text='Aktifkan notifikasi ulang tahun'),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='enable_followup_notif',
            field=models.BooleanField(default=True, help_text='Aktifkan notifikasi follow-up registrasi'),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='enable_inactive_notif',
            field=models.BooleanField(default=True, help_text='Aktifkan notifikasi pasien tidak aktif'),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='inactive_threshold_days',
            field=models.IntegerField(default=30, help_text='Hari inaktif untuk notifikasi pasien (default: 30 hari)'),
        ),
    ]
