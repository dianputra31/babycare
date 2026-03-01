from datetime import date
from django.core.exceptions import ValidationError


def calculate_total_bayar(harga, biaya_transport):
    # assume harga and biaya_transport are Decimal or numeric
    return (harga or 0) + (biaya_transport or 0)


def calculate_age(birth_date: date, reference: date | None = None) -> int:
    if reference is None:
        reference = date.today()
    if birth_date is None:
        return 0
    years = reference.year - birth_date.year
    if (reference.month, reference.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def validate_age_for_terapi(pasien, jenis_terapi, reference_date=None):
    """Raise ValidationError if pasien age not allowed for jenis_terapi."""
    if pasien is None or jenis_terapi is None:
        return
    age = calculate_age(pasien.tanggal_lahir, reference_date)
    if jenis_terapi.kategori_usia_min is not None and age < jenis_terapi.kategori_usia_min:
        raise ValidationError(f"Pasien terlalu muda untuk terapi '{jenis_terapi.nama_terapi}' (umur {age} < min {jenis_terapi.kategori_usia_min})")
    if jenis_terapi.kategori_usia_max is not None and age > jenis_terapi.kategori_usia_max:
        raise ValidationError(f"Pasien melebihi batas umur untuk terapi '{jenis_terapi.nama_terapi}' (umur {age} > max {jenis_terapi.kategori_usia_max})")
