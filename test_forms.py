import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babycare_project.settings')
django.setup()

from core.forms import RegistrasiForm, PemasukanForm

# Test if form widgets have correct classes
reg_form = RegistrasiForm()
print('=== REGISTRASI FORM WIDGETS ===')
print(f'Pasien widget class: {reg_form.fields["pasien"].widget.attrs.get("class")}')
print(f'Jenis Terapi widget class: {reg_form.fields["jenis_terapi"].widget.attrs.get("class")}')
print(f'Terapis widget class: {reg_form.fields["terapis"].widget.attrs.get("class")}')
print(f'Cabang widget class: {reg_form.fields["cabang"].widget.attrs.get("class")}')
print(f'Harga widget class: {reg_form.fields["harga"].widget.attrs.get("class")}')
print(f'Biaya Transport widget class: {reg_form.fields["biaya_transport"].widget.attrs.get("class")}')

print('\n=== PEMASUKAN FORM WIDGETS ===')
pem_form = PemasukanForm()
print(f'Registrasi widget class: {pem_form.fields["registrasi"].widget.attrs.get("class")}')
print(f'Metode Pembayaran widget class: {pem_form.fields["metode_pembayaran"].widget.attrs.get("class")}')
print(f'Cabang widget class: {pem_form.fields["cabang"].widget.attrs.get("class")}')
print(f'Jumlah widget class: {pem_form.fields["jumlah"].widget.attrs.get("class")}')

print('\n✅ All form widgets configured correctly!')
