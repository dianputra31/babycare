# Add foreign key constraint for updated_by field

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_appsettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appsettings',
            name='updated_by_id',
        ),
        migrations.AddField(
            model_name='appsettings',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='settings_updated', to=settings.AUTH_USER_MODEL, db_constraint=False),
        ),
    ]
