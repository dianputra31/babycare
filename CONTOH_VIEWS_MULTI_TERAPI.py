"""
Views untuk Registrasi Multi-Terapi
Ganti RegistrasiCreateView dan RegistrasiEditView yang ada dengan kode ini
"""

from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import date

from .models import Registrasi, RegistrasiDetail
from .forms import RegistrasiFormMultiTerapi, RegistrasiDetailFormSet


class RegistrasiCreateViewMultiTerapi(LoginRequiredMixin, CreateView):
    """View untuk Create Registrasi dengan Multi-Terapi"""
    model = Registrasi
    form_class = RegistrasiFormMultiTerapi
    template_name = 'core/registrasi_form_multi.html'
    success_url = reverse_lazy('dashboard')

    def get_initial(self):
        """Set default values for form fields."""
        initial = super().get_initial()
        initial['tanggal_kunjungan'] = date.today()
        return initial

    def get_context_data(self, **kwargs):
        """Add formset to context"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = RegistrasiDetailFormSet(self.request.POST)
        else:
            context['formset'] = RegistrasiDetailFormSet()
        context['is_edit'] = False
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Handle form and formset validation & saving"""
        context = self.get_context_data()
        formset = context['formset']
        
        # Validate formset
        if not formset.is_valid():
            # Debug: print formset errors
            print("Formset errors:", formset.errors)
            print("Formset non_form_errors:", formset.non_form_errors())
            
            messages.error(self.request, 'Terjadi kesalahan pada data terapi. Periksa kembali input Anda.')
            return self.form_invalid(form)
        
        # Generate kode_registrasi
        if not form.instance.kode_registrasi:
            today = date.today()
            cabang_id = form.instance.cabang_id
            
            # Format: P + CABANG_ID(2digit) + MMYY + sequential number (3 digits)
            cabang_code = f'{cabang_id:02d}' if cabang_id else '00'
            month_year = today.strftime('%m%y')
            prefix = f'P{cabang_code}{month_year}'
            
            # Get the highest sequence number for this cabang/month/year
            last_registrasi = Registrasi.objects.filter(
                kode_registrasi__startswith=prefix,
                cabang_id=cabang_id
            ).order_by('-kode_registrasi', '-id').first()
            
            if last_registrasi and last_registrasi.kode_registrasi:
                try:
                    last_seq = int(last_registrasi.kode_registrasi[-3:])
                    next_seq = last_seq + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
            
            form.instance.kode_registrasi = f'{prefix}{next_seq:03d}'
        
        # Calculate total harga from all terapi in formset
        total_harga = Decimal('0.00')
        for detail_form in formset:
            if detail_form.cleaned_data and not detail_form.cleaned_data.get('DELETE'):
                jenis_terapi = detail_form.cleaned_data.get('jenis_terapi')
                if jenis_terapi:
                    total_harga += jenis_terapi.harga
        
        # Set harga and total_bayar
        form.instance.harga = total_harga
        biaya_transport = form.instance.biaya_transport or Decimal('0.00')
        form.instance.total_bayar = total_harga + biaya_transport
        
        # Set created_by
        form.instance.created_by = self.request.user
        
        # Save registrasi (header)
        self.object = form.save()
        
        # Save detail terapi
        formset.instance = self.object
        details = formset.save(commit=False)
        
        for detail in details:
            detail.registrasi = self.object
            detail.kode_registrasi = self.object.kode_registrasi
            detail.nama_terapi = detail.jenis_terapi.nama_terapi
            detail.harga_terapi = detail.jenis_terapi.harga
            detail.save()
        
        # Delete any marked for deletion
        for obj in formset.deleted_objects:
            obj.delete()
        
        messages.success(self.request, f'Registrasi berhasil disimpan! Kode: {self.object.kode_registrasi}')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        # Create detailed error message
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields.get(field, type('obj', (), {'label': field})).label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)


class RegistrasiEditViewMultiTerapi(LoginRequiredMixin, UpdateView):
    """View untuk Edit Registrasi dengan Multi-Terapi"""
    model = Registrasi
    form_class = RegistrasiFormMultiTerapi
    template_name = 'core/registrasi_form_multi.html'
    success_url = reverse_lazy('registrasi_list')

    def get_context_data(self, **kwargs):
        """Add formset to context"""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = RegistrasiDetailFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = RegistrasiDetailFormSet(instance=self.object)
        context['is_edit'] = True
        return context

    @transaction.atomic
    def form_valid(self, form):
        """Handle form and formset validation & saving"""
        context = self.get_context_data()
        formset = context['formset']
        
        # Validate formset
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            print("Formset non_form_errors:", formset.non_form_errors())
            
            messages.error(self.request, 'Terjadi kesalahan pada data terapi. Periksa kembali input Anda.')
            return self.form_invalid(form)
        
        # Calculate total harga from all terapi in formset
        total_harga = Decimal('0.00')
        for detail_form in formset:
            if detail_form.cleaned_data and not detail_form.cleaned_data.get('DELETE'):
                jenis_terapi = detail_form.cleaned_data.get('jenis_terapi')
                if jenis_terapi:
                    total_harga += jenis_terapi.harga
        
        # Update harga and total_bayar
        form.instance.harga = total_harga
        biaya_transport = form.instance.biaya_transport or Decimal('0.00')
        form.instance.total_bayar = total_harga + biaya_transport
        
        # Save registrasi (header)
        self.object = form.save()
        
        # Save detail terapi
        formset.instance = self.object
        details = formset.save(commit=False)
        
        for detail in details:
            detail.registrasi = self.object
            detail.kode_registrasi = self.object.kode_registrasi
            detail.nama_terapi = detail.jenis_terapi.nama_terapi
            detail.harga_terapi = detail.jenis_terapi.harga
            detail.save()
        
        # Delete any marked for deletion
        for obj in formset.deleted_objects:
            obj.delete()
        
        messages.success(self.request, f'Registrasi berhasil diupdate! Kode: {self.object.kode_registrasi}')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors"""
        error_messages = []
        for field, errors in form.errors.items():
            if field == '__all__':
                error_messages.extend(errors)
            else:
                field_label = form.fields.get(field, type('obj', (), {'label': field})).label or field
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
        
        if error_messages:
            messages.error(self.request, 'Terjadi kesalahan:<br>' + '<br>'.join(error_messages))
        else:
            messages.error(self.request, 'Terjadi kesalahan. Periksa kembali data yang diinput.')
        
        return super().form_invalid(form)


# API Endpoint untuk AJAX - Get Harga Terapi
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

@login_required
@require_http_methods(["GET"])
def api_jenis_terapi_detail(request, pk):
    """API endpoint untuk get detail jenis terapi (untuk AJAX)"""
    from .models import JenisTerapi
    
    try:
        terapi = JenisTerapi.objects.get(pk=pk, is_deleted=False)
        return JsonResponse({
            'id': terapi.id,
            'nama_terapi': terapi.nama_terapi,
            'harga': float(terapi.harga),
            'harga_formatted': f'Rp {int(terapi.harga):,}'.replace(',', '.')
        })
    except JenisTerapi.DoesNotExist:
        return JsonResponse({'error': 'Terapi tidak ditemukan'}, status=404)
