"""
Django management command to automatically generate notifications.

Generates notifications for:
1. Birthday reminders (when patient's birth date matches today's day/month)
2. Upcoming therapy (7 days before tanggal_kunjungan)
3. Tomorrow's therapy (1 day before tanggal_kunjungan)
4. Today's therapy schedule
5. 30-day inactive patients

Usage:
    python manage.py generate_notifications
    python manage.py generate_notifications --dry-run
    
Schedule this command to run daily at midnight using:
- Windows Task Scheduler
- Cron job (Linux/Mac)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Pasien, Registrasi, Notifikasi


class Command(BaseCommand):
    help = 'Generate automatic notifications for birthdays, therapy reminders, and inactive patients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview notifications without creating them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        # Counters
        birthday_count = 0
        today_therapy_count = 0
        upcoming_therapy_count = 0
        tomorrow_therapy_count = 0
        inactive_count = 0
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Generate Notifications ({today}) ===\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No notifications will be created\n'))
        
        # ========================================
        # 1. BIRTHDAY NOTIFICATIONS
        # ========================================
        self.stdout.write('Checking birthday notifications...')
        
        pasien_list = Pasien.objects.filter(
            is_deleted=False,
            tanggal_lahir__isnull=False
        )
        
        for pasien in pasien_list:
            # Check if birthday matches today (day and month only)
            if pasien.tanggal_lahir.day == today.day and pasien.tanggal_lahir.month == today.month:
                # Calculate age
                age = today.year - pasien.tanggal_lahir.year
                
                # Check if notification already exists
                exists = Notifikasi.objects.filter(
                    pasien=pasien,
                    jenis_notifikasi='Ulang Tahun',
                    tanggal_notifikasi=today
                ).exists()
                
                if not exists:
                    pesan = f'🎂 Hari ini ulang tahun {pasien.nama_anak} yang ke-{age}! Jangan lupa ucapkan selamat.'
                    
                    if not dry_run:
                        Notifikasi.objects.create(
                            pasien=pasien,
                            jenis_notifikasi='Ulang Tahun',
                            pesan=pesan,
                            tanggal_notifikasi=today,
                            sudah_dibaca=False
                        )
                    
                    birthday_count += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Birthday: {pasien.nama_anak} ({age} tahun)'))
        
        # ========================================
        # 2. TODAY'S THERAPY SCHEDULE
        # ========================================
        self.stdout.write('\nChecking today\'s therapy schedule...')
        
        registrasi_list_today = Registrasi.objects.filter(
            is_deleted=False,
            tanggal_kunjungan=today,
            status__in=['BOOKED', 'CONFIRMED']
        ).select_related('pasien', 'jenis_terapi', 'terapis')
        
        for registrasi in registrasi_list_today:
            # Check if notification already exists
            exists = Notifikasi.objects.filter(
                pasien=registrasi.pasien,
                registrasi=registrasi,
                jenis_notifikasi='Jadwal Hari Ini',
                tanggal_notifikasi=today
            ).exists()
            
            if not exists:
                terapis_name = registrasi.terapis.nama_terapis if registrasi.terapis else 'Terapis belum ditentukan'
                pesan = (
                    f'📋 Hari ini: {registrasi.pasien.nama_anak} memiliki jadwal terapi '
                    f'{registrasi.jenis_terapi.nama_terapi} dengan {terapis_name}.'
                )
                
                if not dry_run:
                    Notifikasi.objects.create(
                        pasien=registrasi.pasien,
                        registrasi=registrasi,
                        jenis_notifikasi='Jadwal Hari Ini',
                        pesan=pesan,
                        tanggal_notifikasi=today,
                        sudah_dibaca=False
                    )
                
                today_therapy_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Today: {registrasi.pasien.nama_anak} - {registrasi.jenis_terapi.nama_terapi}'
                ))
        
        # ========================================
        # 3. UPCOMING THERAPY (7 DAYS AHEAD)
        # ========================================
        self.stdout.write('\nChecking upcoming therapy notifications (7 days)...')
        
        target_date_7days = today + timedelta(days=7)
        
        registrasi_list_7days = Registrasi.objects.filter(
            is_deleted=False,
            tanggal_kunjungan=target_date_7days,
            status__in=['BOOKED', 'CONFIRMED']
        ).select_related('pasien', 'jenis_terapi', 'terapis')
        
        for registrasi in registrasi_list_7days:
            # Check if notification already exists
            exists = Notifikasi.objects.filter(
                pasien=registrasi.pasien,
                registrasi=registrasi,
                jenis_notifikasi='Reminder Terapi',
                tanggal_notifikasi=today
            ).exists()
            
            if not exists:
                terapis_name = registrasi.terapis.nama_terapis if registrasi.terapis else 'Terapis belum ditentukan'
                pesan = (
                    f'📅 Reminder: Pasien {registrasi.pasien.nama_anak} memiliki jadwal terapi '
                    f'{registrasi.jenis_terapi.nama_terapi} pada {target_date_7days.strftime("%d %B %Y")} '
                    f'dengan {terapis_name}.'
                )
                
                if not dry_run:
                    Notifikasi.objects.create(
                        pasien=registrasi.pasien,
                        registrasi=registrasi,
                        jenis_notifikasi='Reminder Terapi',
                        pesan=pesan,
                        tanggal_notifikasi=today,
                        sudah_dibaca=False
                    )
                
                upcoming_therapy_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Reminder 7 days: {registrasi.pasien.nama_anak} - {registrasi.jenis_terapi.nama_terapi}'
                ))
        
        # ========================================
        # 4. TOMORROW'S THERAPY
        # ========================================
        self.stdout.write('\nChecking tomorrow\'s therapy notifications...')
        
        tomorrow = today + timedelta(days=1)
        
        registrasi_list_tomorrow = Registrasi.objects.filter(
            is_deleted=False,
            tanggal_kunjungan=tomorrow,
            status__in=['BOOKED', 'CONFIRMED']
        ).select_related('pasien', 'jenis_terapi', 'terapis')
        
        for registrasi in registrasi_list_tomorrow:
            # Check if notification already exists
            exists = Notifikasi.objects.filter(
                pasien=registrasi.pasien,
                registrasi=registrasi,
                jenis_notifikasi='Besok Terapi',
                tanggal_notifikasi=today
            ).exists()
            
            if not exists:
                terapis_name = registrasi.terapis.nama_terapis if registrasi.terapis else 'Terapis belum ditentukan'
                pesan = (
                    f'⏰ Besok ({tomorrow.strftime("%d %B %Y")}): '
                    f'{registrasi.pasien.nama_anak} akan terapi {registrasi.jenis_terapi.nama_terapi} '
                    f'dengan {terapis_name}.'
                )
                
                if not dry_run:
                    Notifikasi.objects.create(
                        pasien=registrasi.pasien,
                        registrasi=registrasi,
                        jenis_notifikasi='Besok Terapi',
                        pesan=pesan,
                        tanggal_notifikasi=today,
                        sudah_dibaca=False
                    )
                
                tomorrow_therapy_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f'  ✓ Tomorrow: {registrasi.pasien.nama_anak} - {registrasi.jenis_terapi.nama_terapi}'
                ))
        
        # ========================================
        # 5. 30-DAY INACTIVE PATIENTS
        # ========================================
        self.stdout.write('\nChecking 30-day inactive patients...')
        
        threshold_date = today - timedelta(days=30)
        
        # Get all active patients
        all_pasien = Pasien.objects.filter(is_deleted=False)
        
        for pasien in all_pasien:
            # Get last registration
            last_reg = Registrasi.objects.filter(
                pasien=pasien,
                is_deleted=False
            ).order_by('-tanggal_kunjungan').first()
            
            if last_reg is None:
                # Patient has never had a registration
                exists = Notifikasi.objects.filter(
                    pasien=pasien,
                    jenis_notifikasi='Pasien Tidak Aktif',
                    tanggal_notifikasi=today
                ).exists()
                
                if not exists:
                    pesan = f'⚠️ Pasien {pasien.nama_anak} belum pernah melakukan registrasi terapi.'
                    
                    if not dry_run:
                        Notifikasi.objects.create(
                            pasien=pasien,
                            jenis_notifikasi='Pasien Tidak Aktif',
                            pesan=pesan,
                            tanggal_notifikasi=today,
                            sudah_dibaca=False
                        )
                    
                    inactive_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Inactive: {pasien.nama_anak} (belum pernah registrasi)'
                    ))
            elif last_reg.tanggal_kunjungan <= threshold_date:
                # Last visit was more than 30 days ago
                exists = Notifikasi.objects.filter(
                    pasien=pasien,
                    jenis_notifikasi='Pasien Tidak Aktif',
                    tanggal_notifikasi=today
                ).exists()
                
                if not exists:
                    days_inactive = (today - last_reg.tanggal_kunjungan).days
                    pesan = (
                        f'⚠️ Pasien {pasien.nama_anak} sudah {days_inactive} hari tidak kembali. '
                        f'Terakhir terapi: {last_reg.tanggal_kunjungan.strftime("%d %B %Y")}.'
                    )
                    
                    if not dry_run:
                        Notifikasi.objects.create(
                            pasien=pasien,
                            jenis_notifikasi='Pasien Tidak Aktif',
                            pesan=pesan,
                            tanggal_notifikasi=today,
                            sudah_dibaca=False
                        )
                    
                    inactive_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Inactive: {pasien.nama_anak} ({days_inactive} hari)'
                    ))
        
        # ========================================
        # SUMMARY
        # ========================================
        total = birthday_count + today_therapy_count + upcoming_therapy_count + tomorrow_therapy_count + inactive_count
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'\n✅ SUMMARY:'))
        self.stdout.write(f'  🎂 Birthday notifications: {birthday_count}')
        self.stdout.write(f'  📋 Today\'s therapy: {today_therapy_count}')
        self.stdout.write(f'  📅 7-day reminders: {upcoming_therapy_count}')
        self.stdout.write(f'  ⏰ Tomorrow therapy: {tomorrow_therapy_count}')
        self.stdout.write(f'  ⚠️  30-day inactive: {inactive_count}')
        self.stdout.write(f'  📊 TOTAL: {total} notifications')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN - No changes made to database'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Notifications created successfully!'))
        
        self.stdout.write('\n' + '='*50 + '\n')
