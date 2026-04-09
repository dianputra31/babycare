# Generated migration for inventory management system

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_progresstracking'),
    ]

    operations = [
        migrations.CreateModel(
            name='KategoriBarang',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('nama_kategori', models.CharField(db_column='nama_kategori', max_length=100)),
                ('deskripsi', models.TextField(blank=True, db_column='deskripsi', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at')),
            ],
            options={
                'db_table': 'kategori_barang',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='BarangInventory',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('kode_barang', models.CharField(blank=True, db_column='kode_barang', max_length=20, null=True, unique=True)),
                ('nama_barang', models.CharField(db_column='nama_barang', max_length=200)),
                ('satuan', models.CharField(db_column='satuan', max_length=20, help_text='pcs, box, set, dll')),
                ('stok_minimum', models.IntegerField(db_column='stok_minimum', default=5, help_text='Alert jika stok dibawah nilai ini')),
                ('stok_tersedia', models.IntegerField(db_column='stok_tersedia', default=0)),
                ('harga_satuan', models.DecimalField(db_column='harga_satuan', decimal_places=2, default=0, help_text='Harga per satuan', max_digits=12)),
                ('lokasi_penyimpanan', models.CharField(blank=True, db_column='lokasi_penyimpanan', max_length=100, null=True)),
                ('catatan', models.TextField(blank=True, db_column='catatan', null=True)),
                ('is_active', models.BooleanField(db_column='is_active', default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('updated_at', models.DateTimeField(auto_now=True, db_column='updated_at')),
                ('kategori', models.ForeignKey(blank=True, db_column='kategori_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.kategoribarang')),
                ('cabang', models.ForeignKey(blank=True, db_column='cabang_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.cabang')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barang_created', to='core.user')),
            ],
            options={
                'db_table': 'barang_inventory',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StokMasuk',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('tanggal_masuk', models.DateField(db_column='tanggal_masuk')),
                ('jumlah', models.IntegerField(db_column='jumlah')),
                ('harga_beli_satuan', models.DecimalField(blank=True, db_column='harga_beli_satuan', decimal_places=2, max_digits=12, null=True)),
                ('supplier', models.CharField(blank=True, db_column='supplier', max_length=200, null=True)),
                ('no_faktur', models.CharField(blank=True, db_column='no_faktur', max_length=50, null=True)),
                ('catatan', models.TextField(blank=True, db_column='catatan', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('barang', models.ForeignKey(db_column='barang_id', on_delete=django.db.models.deletion.CASCADE, related_name='stok_masuk_entries', to='core.baranginventory')),
                ('cabang', models.ForeignKey(blank=True, db_column='cabang_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.cabang')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='stok_masuk_created', to='core.user')),
            ],
            options={
                'db_table': 'stok_masuk',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='PemakaianBarang',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('tanggal_pakai', models.DateField(db_column='tanggal_pakai')),
                ('jumlah', models.IntegerField(db_column='jumlah')),
                ('tujuan', models.CharField(db_column='tujuan', help_text='Untuk apa barang dipakai', max_length=200)),
                ('catatan', models.TextField(blank=True, db_column='catatan', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at')),
                ('barang', models.ForeignKey(db_column='barang_id', on_delete=django.db.models.deletion.CASCADE, related_name='pemakaian_entries', to='core.baranginventory')),
                ('registrasi', models.ForeignKey(blank=True, db_column='registrasi_id', help_text='Jika pemakaian terkait sesi terapi', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='barang_dipakai', to='core.registrasi')),
                ('cabang', models.ForeignKey(blank=True, db_column='cabang_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='core.cabang')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pemakaian_barang_created', to='core.user')),
            ],
            options={
                'db_table': 'pemakaian_barang',
                'managed': True,
            },
        ),
    ]
