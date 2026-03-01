# Generated manually for AppSettings model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('font_size', models.IntegerField(default=14, help_text='Font size in pixels (default: 14)')),
                ('logo', models.ImageField(blank=True, help_text='Upload logo image', null=True, upload_to='logos/')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by_id', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'App Settings',
                'verbose_name_plural': 'App Settings',
                'db_table': 'app_settings',
            },
        ),
    ]
