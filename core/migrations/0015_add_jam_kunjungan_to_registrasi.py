from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_add_theme_to_appsettings'),
    ]

    operations = [
        # Add field to Django state (managed=False model)
        migrations.AddField(
            model_name='registrasi',
            name='jam_kunjungan',
            field=models.TimeField(blank=True, db_column='jam_kunjungan', null=True),
        ),
        # Add column to actual database table
        migrations.RunSQL(
            sql="ALTER TABLE registrasi ADD COLUMN IF NOT EXISTS jam_kunjungan TIME NULL;",
            reverse_sql="ALTER TABLE registrasi DROP COLUMN IF EXISTS jam_kunjungan;",
        ),
    ]
