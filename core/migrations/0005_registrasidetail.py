# Generated migration for RegistrasiDetail model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_notification_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrasiDetail',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('kode_registrasi', models.CharField(blank=True, db_column='kode_registrasi', max_length=255, null=True)),
                ('nama_terapi', models.CharField(blank=True, db_column='nama_terapi', max_length=255, null=True)),
                ('harga_terapi', models.DecimalField(blank=True, db_column='harga_terapi', decimal_places=0, max_digits=12, null=True)),
                ('remark', models.CharField(blank=True, db_column='remark', max_length=255, null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, db_column='created_date')),
                ('remark2', models.CharField(blank=True, db_column='remark2', max_length=255, null=True)),
                ('remark3', models.CharField(blank=True, db_column='remark3', max_length=255, null=True)),
                ('jenis_terapi', models.ForeignKey(db_column='id_terapi', on_delete=django.db.models.deletion.DO_NOTHING, to='core.jenisterapi')),
                ('registrasi', models.ForeignKey(db_column='registrasi_id', on_delete=django.db.models.deletion.CASCADE, related_name='details', to='core.registrasi')),
            ],
            options={
                'db_table': 'registrasi_detail',
                'managed': False,
            },
        ),
    ]
