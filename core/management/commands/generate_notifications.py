"""
Django management command to automatically generate notifications.

Generates notifications for:
1. Birthday reminders (configurable H-1, H-2, etc)
2. Inactive patients (configurable 1, 3, 6, 12 months)
3. Follow-up for recent registrations
4. High-potential customers
5. Appointment reminders

Usage:
    python manage.py generate_notifications
    python manage.py generate_notifications --type birthday
    python manage.py generate_notifications --all
    
Schedule this command to run daily at midnight using:
- Windows Task Scheduler
- Cron job (Linux/Mac)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.services.notification_service import (
    generate_all_notifications,
    create_birthday_notifications,
    create_inactive_patient_notifications,
    create_followup_notifications,
    create_high_potential_notifications,
    create_scheduled_appointment_reminders,
)


class Command(BaseCommand):
    help = 'Generate automatic notifications for birthdays, inactive patients, and more'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['birthday', 'inactive', 'followup', 'high_potential', 'appointment_reminder', 'all'],
            default='all',
            help='Type of notification to generate',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate all types of notifications',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        notif_type = options['type'] if not options['all'] else 'all'
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Generate Notifications ({today}) ===\n'))
        
        try:
            if notif_type == 'all':
                result = generate_all_notifications()
                self.display_results(result)
            elif notif_type == 'birthday':
                result = create_birthday_notifications()
                self.stdout.write(f"Birthday Notifications: {result['message']}")
            elif notif_type == 'inactive':
                result = create_inactive_patient_notifications()
                self.stdout.write(f"Inactive Patient Notifications: {result['message']}")
            elif notif_type == 'followup':
                result = create_followup_notifications()
                self.stdout.write(f"Follow-up Notifications: {result['message']}")
            elif notif_type == 'high_potential':
                result = create_high_potential_notifications()
                self.stdout.write(f"High-Potential Customer Notifications: {result['message']}")
            elif notif_type == 'appointment_reminder':
                result = create_scheduled_appointment_reminders()
                self.stdout.write(f"Appointment Reminder Notifications: {result['message']}")
            
            self.stdout.write(self.style.SUCCESS('\n✓ Notification generation completed!\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error generating notifications: {str(e)}\n'))
            raise

    def display_results(self, result):
        """Display results in a formatted table"""
        self.stdout.write(
            self.style.SUCCESS(f"\nTotal notifications created: {result['total_created']}\n")
        )
        
        for notif_type, data in result['details'].items():
            self.stdout.write(
                f"  • {notif_type.upper()}: {data['created']} created - {data['message']}"
            )
        
        self.stdout.write(f"\nTimestamp: {result['timestamp']}\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No notifications will be created\n'))
        
        # ========================================
        # 1. BIRTHDAY, INACTIVE, PENDING PAYMENT NOTIFICATIONS
        # ========================================
        self.stdout.write('Generating birthday, inactive, and pending payment notifications...')
        if not dry_run:
            notif_results = NotificationService.generate_all_notifications()
            birthday_count = notif_results['birthday']['count']
            inactive_count = notif_results['inactive']['count']
            pending_payment_count = notif_results['pending_payment']['count']
            self.stdout.write(self.style.SUCCESS(f"✓ {notif_results['birthday']['message']}"))
            self.stdout.write(self.style.SUCCESS(f"✓ {notif_results['inactive']['message']}"))
            self.stdout.write(self.style.SUCCESS(f"✓ {notif_results['pending_payment']['message']}"))
        else:
            self.stdout.write(self.style.WARNING('DRY RUN: No notifications created for birthday, inactive, or pending payment'))

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
        total = birthday_count + today_therapy_count + upcoming_therapy_count + tomorrow_therapy_count + inactive_count + pending_payment_count
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'\n✅ SUMMARY:'))
        self.stdout.write(f'  🎂 Birthday notifications: {birthday_count}')
        self.stdout.write(f'  ⚠️ Inactive: {inactive_count}')
        self.stdout.write(f'  💸 Pending payment: {pending_payment_count}')
        self.stdout.write(f'  📋 Today\'s therapy: {today_therapy_count}')
        self.stdout.write(f'  📅 7-day reminders: {upcoming_therapy_count}')
        self.stdout.write(f'  ⏰ Tomorrow therapy: {tomorrow_therapy_count}')
        self.stdout.write(f'  📊 TOTAL: {total} notifications')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  DRY RUN - No changes made to database'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Notifications created successfully!'))
        
        self.stdout.write('\n' + '='*50 + '\n')

        # Manual trigger button logic (for web UI):
        # You can expose a view that calls NotificationService.generate_all_notifications() when user clicks a button
        # Example: /notifikasi/generate/ (POST request)
        # See notification_service.py for details
