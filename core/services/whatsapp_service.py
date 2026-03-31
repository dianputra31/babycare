# e:/projects/python/django/teguh/babycare/core/services/whatsapp_service.py
import requests
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service untuk mengirim WhatsApp messages via Fonnte API"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'FONNTE_API_KEY', None)
        self.api_url = "https://api.fonnte.com/send"
    
    def is_configured(self):
        """Check if WhatsApp service is configured"""
        return bool(self.api_key)
    
    def format_phone_number(self, phone):
        """
        Format nomor telepon untuk WhatsApp API
        Input: 08123456789 atau 8123456789 atau +628123456789
        Output: 628123456789
        """
        if not phone:
            return None
        
        # Remove whitespace and special chars
        phone = phone.strip().replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        
        # Remove leading +
        if phone.startswith('+'):
            phone = phone[1:]
        
        # Convert 08xx to 628xx
        if phone.startswith('08'):
            phone = '62' + phone[1:]
        elif phone.startswith('8'):
            phone = '62' + phone
        
        return phone
    
    def send_appointment_reminder(self, registrasi):
        """
        Send appointment reminder via WhatsApp
        
        Args:
            registrasi: Registrasi object
            
        Returns:
            dict: {'success': bool, 'message': str, 'response': dict}
        """
        if not self.is_configured():
            return {
                'success': False,
                'message': 'WhatsApp service belum dikonfigurasi. Tambahkan FONNTE_API_KEY di .env',
                'response': None
            }
        
        # Check if patient has WhatsApp
        pasien = registrasi.pasien
        if not pasien.has_whatsapp or not pasien.no_wa:
            return {
                'success': False,
                'message': f'Pasien {pasien.nama_anak} tidak memiliki nomor WhatsApp',
                'response': None
            }
        
        # Format phone number
        phone = self.format_phone_number(pasien.no_wa)
        if not phone:
            return {
                'success': False,
                'message': 'Nomor WhatsApp tidak valid',
                'response': None
            }
        
        # Build reminder message
        tanggal_str = registrasi.tanggal_kunjungan.strftime('%d %B %Y')
        hari_str = self._get_day_name(registrasi.tanggal_kunjungan)
        
        # Get therapy names
        therapies = registrasi.details.all()
        therapy_list = ', '.join([detail.jenis_terapi.nama_terapi for detail in therapies])
        
        terapis_name = registrasi.terapis.nama_terapis if registrasi.terapis else 'Terapis'
        cabang_name = registrasi.cabang.nama_cabang if registrasi.cabang else ''
        
        message = f"""🏥 *Reminder Appointment BabyCare*

Yth. {pasien.nama_orang_tua or 'Bapak/Ibu'},

Ini adalah pengingat appointment untuk:
👶 *Anak*: {pasien.nama_anak}
📅 *Tanggal*: {hari_str}, {tanggal_str}
💆 *Terapi*: {therapy_list}
🧑‍⚕️ *Terapis*: {terapis_name}
🏢 *Cabang*: {cabang_name}

Mohon konfirmasi kehadiran atau hubungi kami jika ada perubahan jadwal.

Terima kasih! 🙏
_BabyCare Team_"""
        
        # Send via Fonnte API
        try:
            headers = {
                'Authorization': self.api_key
            }
            
            data = {
                'target': phone,
                'message': message,
                'countryCode': '62'
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                data=data,
                timeout=30
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get('status'):
                logger.info(f"WhatsApp reminder sent to {phone} for registrasi {registrasi.id}")
                return {
                    'success': True,
                    'message': f'Reminder berhasil dikirim ke {pasien.no_wa}',
                    'response': result
                }
            else:
                error_msg = result.get('reason') or result.get('message') or 'Unknown error'
                logger.error(f"Failed to send WhatsApp: {error_msg}")
                return {
                    'success': False,
                    'message': f'Gagal mengirim WhatsApp: {error_msg}',
                    'response': result
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"WhatsApp API timeout for registrasi {registrasi.id}")
            return {
                'success': False,
                'message': 'Timeout saat mengirim WhatsApp. Coba lagi.',
                'response': None
            }
        except Exception as e:
            logger.error(f"WhatsApp error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}',
                'response': None
            }
    
    def _get_day_name(self, date):
        """Get Indonesian day name"""
        days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        return days[date.weekday()]
    
    def send_bulk_reminders(self, registrasi_list):
        """
        Send reminders to multiple registrations
        
        Returns:
            dict: {'success_count': int, 'failed_count': int, 'results': list}
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for registrasi in registrasi_list:
            result = self.send_appointment_reminder(registrasi)
            results.append({
                'registrasi_id': registrasi.id,
                'pasien': registrasi.pasien.nama_anak,
                **result
            })
            
            if result['success']:
                success_count += 1
            else:
                failed_count += 1
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'results': results
        }


# Singleton instance
whatsapp_service = WhatsAppService()
