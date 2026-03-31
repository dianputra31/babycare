"""
Management Command untuk Migrasi Data Lama ke Sistem Multi-Terapi
Simpan file ini di: core/management/commands/migrate_to_multiterapi.py
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Registrasi, RegistrasiDetail


class Command(BaseCommand):
    help = 'Migrate existing single-therapy registrasi to multi-therapy registrasi_detail'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually migrating',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if details already exist',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(self.style.WARNING('Starting migration...'))
        
        # Get all registrasi that don't have is_deleted=True
        registrasis = Registrasi.objects.filter(is_deleted=False).select_related('jenis_terapi')
        total_count = registrasis.count()
        
        self.stdout.write(f'Found {total_count} registrasi records')
        
        migrated = 0
        skipped = 0
        errors = 0
        
        for reg in registrasis:
            try:
                # Check if already has details
                has_details = reg.details.exists()
                
                if has_details and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f'  Skipping {reg.kode_registrasi}: Already has {reg.details.count()} detail(s)'
                        )
                    )
                    skipped += 1
                    continue
                
                if has_details and force:
                    # Delete existing details
                    deleted_count = reg.details.count()
                    if not dry_run:
                        reg.details.all().delete()
                    self.stdout.write(
                        self.style.WARNING(
                            f'  {reg.kode_registrasi}: Deleted {deleted_count} existing detail(s) (force mode)'
                        )
                    )
                
                # Check if jenis_terapi exists (old data might not have it)
                if not reg.jenis_terapi:
                    self.stdout.write(
                        self.style.ERROR(
                            f'  Error: {reg.kode_registrasi} has no jenis_terapi - skipping'
                        )
                    )
                    errors += 1
                    continue
                
                # Create detail from old registrasi data
                detail_data = {
                    'registrasi': reg,
                    'kode_registrasi': reg.kode_registrasi,
                    'jenis_terapi': reg.jenis_terapi,
                    'nama_terapi': reg.jenis_terapi.nama_terapi,
                    'harga_terapi': reg.harga,
                    'remark': getattr(reg, 'catatan', None) or '',
                }
                
                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  DRY-RUN: Would create detail for {reg.kode_registrasi} - '
                            f'{reg.jenis_terapi.nama_terapi} (Rp {reg.harga})'
                        )
                    )
                else:
                    RegistrasiDetail.objects.create(**detail_data)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Migrated {reg.kode_registrasi} - '
                            f'{reg.jenis_terapi.nama_terapi} (Rp {reg.harga})'
                        )
                    )
                
                migrated += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  Error migrating {reg.kode_registrasi}: {str(e)}'
                    )
                )
                errors += 1
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('Migration Summary:'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Total registrasi: {total_count}')
        self.stdout.write(self.style.SUCCESS(f'Migrated: {migrated}'))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'Skipped: {skipped}'))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f'Errors: {errors}'))
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nThis was a DRY-RUN. No data was actually migrated.')
            )
            self.stdout.write(
                self.style.WARNING('Run without --dry-run to perform the actual migration.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nMigration completed successfully!')
            )
