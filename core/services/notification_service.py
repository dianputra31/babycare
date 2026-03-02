"""
Notification Service
Generate various business-related notifications for the babycare application
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q, Count, Max
from decimal import Decimal

from core.models import Notifikasi, Pasien, Registrasi, AppSettings


def create_birthday_notifications():
    """
    Create notifications for patients with upcoming birthdays.
    Based on settings: H-2, H-1, or same day
    """
    settings = AppSettings.get_settings()
    if not settings.enable_birthday_notif:
        return {'created': 0, 'message': 'Birthday notifications are disabled'}
    
    today = timezone.now().date()
    target_date = today + timedelta(days=settings.birthday_notif_days_before)
    
    # Find patients with birthdays on target date
    pasiens = Pasien.objects.filter(
        tanggal_lahir__month=target_date.month,
        tanggal_lahir__day=target_date.day
    ).exclude(tanggal_lahir__isnull=True)
    
    created_count = 0
    for pasien in pasiens:
        # Check if notification already exists for today
        existing = Notifikasi.objects.filter(
            pasien=pasien,
            jenis_notifikasi='BIRTHDAY',
            created_at__date=today
        ).exists()
        
        if not existing:
            age = today.year - pasien.tanggal_lahir.year
            pesan = f"🎂 {pasien.nama_anak} akan berulang tahun dalam {settings.birthday_notif_days_before} hari! Umur {age + 1} tahun. Jangan lupa kirim ucapan atau penawaran special!"
            
            Notifikasi.objects.create(
                pasien=pasien,
                jenis_notifikasi='BIRTHDAY',
                pesan=pesan,
                tanggal_notifikasi=today,
                sudah_dibaca=False
            )
            created_count += 1
    
    return {
        'created': created_count,
        'message': f'Created {created_count} birthday notification(s)'
    }


def create_inactive_patient_notifications():
    """
    Create notifications for patients who haven't had registration for a while.
    Multiple thresholds: 1 month, 3 months, 6 months
    """
    settings = AppSettings.get_settings()
    if not settings.enable_inactive_notif:
        return {'created': 0, 'message': 'Inactive notifications are disabled'}
    
    today = timezone.now().date()
    created_count = 0
    
    # Define inactive thresholds
    thresholds = [
        (30, '1 bulan'),
        (90, '3 bulan'),
        (180, '6 bulan'),
    ]
    
    for days, label in thresholds:
        cutoff_date = today - timedelta(days=days)
        
        # Find patients with last registration before cutoff_date
        inactive_pasiens = Pasien.objects.annotate(
            last_registration_date=Max('registrasi__tanggal_kunjungan')
        ).filter(
            last_registration_date__lt=cutoff_date
        ).exclude(last_registration_date__isnull=True)
        
        for pasien in inactive_pasiens:
            # Check if notification for this threshold already exists for this month
            existing = Notifikasi.objects.filter(
                pasien=pasien,
                jenis_notifikasi=f'INACTIVE_{days}D',
                created_at__year=today.year,
                created_at__month=today.month
            ).exists()
            
            if not existing:
                days_inactive = (today - pasien.registrasi_set.all().aggregate(
                    Max('tanggal_kunjungan')
                )['tanggal_kunjungan__max']).days
                
                pesan = f"⚠️ {pasien.nama_anak} tidak beraktifitas sejak {label} terakhir. Hubungi orang tua untuk follow-up atau penawaran paket special!"
                
                Notifikasi.objects.create(
                    pasien=pasien,
                    jenis_notifikasi=f'INACTIVE_{days}D',
                    pesan=pesan,
                    tanggal_notifikasi=today,
                    sudah_dibaca=False
                )
                created_count += 1
    
    return {
        'created': created_count,
        'message': f'Created {created_count} inactive patient notification(s)'
    }


def create_followup_notifications():
    """
    Create follow-up notifications for recent registrations (within 2 weeks).
    Remind to check patient progress and satisfaction.
    """
    settings = AppSettings.get_settings()
    if not settings.enable_followup_notif:
        return {'created': 0, 'message': 'Follow-up notifications are disabled'}
    
    today = timezone.now().date()
    two_weeks_ago = today - timedelta(days=14)
    created_count = 0
    
    # Find registrations from 7-14 days ago (time to do follow-up)
    target_registrasi = Registrasi.objects.filter(
        tanggal_kunjungan__gte=two_weeks_ago,
        tanggal_kunjungan__lt=today - timedelta(days=3)
    ).select_related('pasien', 'terapis')
    
    for reg in target_registrasi:
        # Check if follow-up notification already exists
        existing = Notifikasi.objects.filter(
            registrasi=reg,
            jenis_notifikasi='FOLLOWUP',
            created_at__date=today
        ).exists()
        
        if not existing:
            pesan = f"📞 Lakukan follow-up untuk {reg.pasien.nama_anak} (terapis: {reg.terapis.nama_terapis if reg.terapis else 'N/A'}). Cek progress dan kepuasan orang tua!"
            
            Notifikasi.objects.create(
                registrasi=reg,
                pasien=reg.pasien,
                jenis_notifikasi='FOLLOWUP',
                pesan=pesan,
                tanggal_notifikasi=today,
                sudah_dibaca=False
            )
            created_count += 1
    
    return {
        'created': created_count,
        'message': f'Created {created_count} follow-up notification(s)'
    }


def create_high_potential_notifications():
    """
    Create notifications for high-value patients or those with high engagement.
    These patients could be upsold to premium packages.
    """
    today = timezone.now().date()
    created_count = 0
    
    # Find pasiens with 5+ registrations in last 3 months
    three_months_ago = today - timedelta(days=90)
    
    high_engagement = Pasien.objects.annotate(
        recent_registrations=Count(
            'registrasi',
            filter=Q(registrasi__tanggal_kunjungan__gte=three_months_ago)
        )
    ).filter(recent_registrations__gte=5)
    
    for pasien in high_engagement:
        # Check if high-potential notification already exists this month
        existing = Notifikasi.objects.filter(
            pasien=pasien,
            jenis_notifikasi='HIGH_POTENTIAL',
            created_at__year=today.year,
            created_at__month=today.month
        ).exists()
        
        if not existing:
            count = pasien.registrasi_set.filter(
                tanggal_kunjungan__gte=three_months_ago
            ).count()
            
            pesan = f"⭐ {pasien.nama_anak} adalah pasien setia dengan {count} sesi dalam 3 bulan terakhir! Tawarkan paket membership atau diskon untuk retensi jangka panjang."
            
            Notifikasi.objects.create(
                pasien=pasien,
                jenis_notifikasi='HIGH_POTENTIAL',
                pesan=pesan,
                tanggal_notifikasi=today,
                sudah_dibaca=False
            )
            created_count += 1
    
    return {
        'created': created_count,
        'message': f'Created {created_count} high-potential customer notification(s)'
    }


def create_scheduled_appointment_reminders():
    """
    Create reminder notifications for appointments scheduled for tomorrow or later this week.
    """
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    end_of_week = today + timedelta(days=7)
    
    created_count = 0
    
    # Find registrations scheduled for this week
    upcoming = Registrasi.objects.filter(
        tanggal_kunjungan__gte=tomorrow,
        tanggal_kunjungan__lte=end_of_week,
        status='BOOKED'
    ).select_related('pasien', 'terapis')
    
    for reg in upcoming:
        # Check if reminder already sent
        existing = Notifikasi.objects.filter(
            registrasi=reg,
            jenis_notifikasi='APPOINTMENT_REMINDER',
            created_at__date=today
        ).exists()
        
        if not existing:
            days_until = (reg.tanggal_kunjungan - today).days
            pesan = f"📅 Appointment reminder: {reg.pasien.nama_anak} dijadwalkan dalam {days_until} hari (Tanggal: {reg.tanggal_kunjungan.strftime('%d-%m-%Y')})"
            
            Notifikasi.objects.create(
                registrasi=reg,
                pasien=reg.pasien,
                jenis_notifikasi='APPOINTMENT_REMINDER',
                pesan=pesan,
                tanggal_notifikasi=today,
                sudah_dibaca=False
            )
            created_count += 1
    
    return {
        'created': created_count,
        'message': f'Created {created_count} appointment reminder(s)'
    }


def generate_all_notifications():
    """
    Master function to generate all notification types at once.
    Can be called by management command or via API.
    """
    results = {
        'birthday': create_birthday_notifications(),
        'inactive': create_inactive_patient_notifications(),
        'followup': create_followup_notifications(),
        'high_potential': create_high_potential_notifications(),
        'appointment_reminder': create_scheduled_appointment_reminders(),
    }
    
    total_created = sum(r['created'] for r in results.values())
    
    return {
        'total_created': total_created,
        'details': results,
        'timestamp': timezone.now()
    }


def cleanup_old_notifications(days=30):
    """
    Delete old notifications that have been read and are older than specified days.
    """
    cutoff_date = timezone.now() - timedelta(days=days)
    deleted_count, _ = Notifikasi.objects.filter(
        sudah_dibaca=True,
        created_at__lt=cutoff_date
    ).delete()
    
    return {
        'deleted': deleted_count,
        'message': f'Deleted {deleted_count} old notification(s)'
    }
