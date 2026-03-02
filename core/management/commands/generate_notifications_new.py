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
